from datetime import datetime
import os

from magic_pdf.data.data_reader_writer import FileBasedDataWriter, FileBasedDataReader
from magic_pdf.data.dataset import PymuDocDataset
from magic_pdf.model.doc_analyze_by_custom_model import doc_analyze
from magic_pdf.config.enums import SupportedPdfParseMethod

from db.database import db_manager
from db.models import FileConvertRecord
from loguru import logger

from utils.formatTime import getDateTime

def pdf2mdjob():
    """
    pdf转md核心任务
    """    
    with db_manager.get_session() as session:
        try:
            pending_records = session.query(FileConvertRecord).filter(FileConvertRecord.status == 2).all()

            if not pending_records:
                return

            logger.info(f"pdf2mdjob:找到 {len(pending_records)} 条待处理的记录。")
            __dir__ = os.path.dirname(os.path.abspath(__file__))

            for record in pending_records:
                try:
                    record.status = 3
                    record.startTime = datetime.now()
                    record.info = f"[{getDateTime()}]开始处理\r\n"+record.info
                    session.commit()
                    logger.info(f"pdf2mdjob:[{record.id}]开始处理")

                    unique_name = os.path.basename(record.originalFilePath)

                     # 准备处理参数
                    name_without_extension = os.path.splitext(unique_name)[0]
                    
                    # 准备输出目录
                    local_image_dir = os.path.join(__dir__, "output", name_without_extension, "images")
                    local_md_dir = os.path.join(__dir__, "output", name_without_extension)
                    image_dir = str(os.path.basename(local_image_dir))
                    os.makedirs(local_image_dir, exist_ok=True)

                    logger.info(f"pdf2mdjob:[{record.id}]:local_image_dir:"+local_image_dir)

                    image_writer, md_writer = FileBasedDataWriter(local_image_dir), FileBasedDataWriter(local_md_dir)

                    reader1 = FileBasedDataReader("")
                    pdf_bytes = reader1.read(record.originalFilePath)

                    ds = PymuDocDataset(pdf_bytes)

                    if ds.classify() == SupportedPdfParseMethod.OCR:
                        infer_result = ds.apply(doc_analyze, ocr=True)
                        pipe_result = infer_result.pipe_ocr_mode(image_writer)
                    else:
                        infer_result = ds.apply(doc_analyze, ocr=False)
                        pipe_result = infer_result.pipe_txt_mode(image_writer)
                    logger.info(f"pdf2mdjob:[{record.id}]:处理完成")
                    record.info = f"[{getDateTime()}]处理完成\r\n"+record.info
                    session.commit()

                    model_inference_result = infer_result.get_infer_res()
                    logger.info(f"pdf2mdjob:[{record.id}]:获取处理结果")
                    record.info = f"[{getDateTime()}]获取处理结果\r\n"+record.info
                    session.commit()

                    pipe_result.draw_layout(os.path.join(local_md_dir, f"{name_without_extension}_layout.pdf"))
                    logger.info(f"pdf2mdjob:[{record.id}]:绘制布局结果")
                    record.info = f"[{getDateTime()}]绘制布局结果\r\n"+record.info
                    session.commit()

                    pipe_result.draw_span(os.path.join(local_md_dir, f"{name_without_extension}_spans.pdf"))
                    logger.info(f"pdf2mdjob:[{record.id}]:绘制span结果")
                    record.info = f"[{getDateTime()}]绘制span结果\r\n"+record.info
                    session.commit()

                    md_content = pipe_result.get_markdown(image_dir)
                    pipe_result.dump_md(md_writer, f"{name_without_extension}.md", image_dir)

                    record.status = 1
                    record.content = md_content
                    record.resultPath = f"/output/{name_without_extension}/{name_without_extension}.md"
                    record.endTime = datetime.now()
                    record.info = f"[{getDateTime()}]转换成功\r\n"+record.info
                    logger.info(f"pdf2mdjob:[{record.id}]转换成功。")

                except Exception as conversion_error:
                    logger.error(f"pdf2mdjob:[{record.id}]发生错误: {conversion_error}", exc_info=True)
                    record.status = 4
                    record.endTime = datetime.now()
                    record.errorMessage = str(conversion_error)
                
                session.commit()

        except Exception as e:
            logger.error(f"pdf2mdjob:执行定时任务时发生数据库错误: {e}", exc_info=True)
            session.rollback()