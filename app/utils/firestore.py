"""
Firestore 에 접근하는 CRUD 인터페이스
"""

from loguru import logger
from google.cloud.firestore import AsyncClient


class FirestoreManager:
    db = AsyncClient()

    @classmethod
    async def set_document(cls, collection_name: str, document_name: str, doc: dict):
        doc_ref = cls.db.collection(collection_name).document(document_name)
        await doc_ref.set(doc)

        return

    @classmethod
    async def update_document(cls, collection_name: str, document_name: str, doc: dict):
        doc_ref = cls.db.collection(collection_name).document(document_name)
        await doc_ref.update(doc)

        return

    @classmethod
    async def get_document(cls, collection_name: str, document_name: str) -> dict:
        """
        {collection_name} 컬렉션에서 {document_name} 에 해당하는 다큐먼트를 가져옴
        """
        doc_ref = cls.db.collection(collection_name).document(document_name)

        doc = await doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        return dict()

    @classmethod
    def get_documents(cls, collection_name: str, key: str, val):
        """
        {collection_name} 컬렉션에서 {key}=={val} 조건을 만족하는 다큐먼트들을 스트림으로 가져옴.
        """
        return cls.db.collection(collection_name).where(key, "==", val).stream()

    @classmethod
    def get_all_documents(cls, collection_name: str):
        return cls.db.collection(collection_name).stream()

    @classmethod
    def get_subcollection_document(
        cls, collection_name: str, document_name: str, subcollection_name: str
    ):
        first_doc = cls.db.collection(collection_name).document(document_name)
        second_doc = first_doc.collection(subcollection_name)
        return second_doc.stream()
