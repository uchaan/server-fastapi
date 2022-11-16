"""
앱 SNS 게시물에 대한 Firestore 업데이트를 담당하는 모듈.
사용자가 프로필 이미지 업데이트 하면 그 사용자의 SNS 게시물에 달려있는 사용자 사진도 모두 업데이트 해줘야함. 
"""

from loguru import logger

from app.utils.firestore import FirestoreManager


class SnsManager:
    @staticmethod
    async def update_posts_img(username, img_url):
        async for doc in FirestoreManager.get_documents(
            "posts", "posterName", username
        ):
            doc_dict = doc.to_dict()
            logger.info(f"{doc.id}: {doc_dict['posterImg']} -> {img_url}")

            doc_dict["posterImg"] = img_url

            await FirestoreManager.set_document("posts", str(doc.id), doc_dict)
