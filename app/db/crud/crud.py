"""
MongoDB에 접근하는 CRUD 인터페이스  
"""
import motor.motor_asyncio

from fastapi.encoders import jsonable_encoder

from loguru import logger

from app.core.config import settings


class Crud:
    client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URL)

    # db named crayon
    db = client.crayon

    @classmethod
    async def add(cls, obj, collection_name: str):
        """
        :param obj: collection 에 집어넣을 document object (e.g. User, Review, Book...)
        :param collection_name: 대상 collection 의 이름 (e.g. 'users', 'reviews', 'books'...)
        :return: 생성된 obj
        """
        collection = cls.db[collection_name]

        obj = jsonable_encoder(obj)

        new_obj = await collection.insert_one(obj)
        logger.info(
            f"[MongoDB][{collection_name}]\t new object's id: {new_obj.inserted_id}"
        )
        created_obj = await collection.find_one({"_id": new_obj.inserted_id})

        return created_obj

    @classmethod
    async def get(cls, id: str, id_name: str, collection_name: str):
        """
        :param id: collection 에서 찾고싶은 object 의 id
        :param id_name: object 내에서 id 의 필드명 (e.g. uid, rid, pid, ...)
        :param collection_name: 대상 collection 의 이름 (e.g. 'users', 'reviews', 'books'...)
        :return: 찾아낸 obj
        """
        collection = cls.db[collection_name]
        if obj := await collection.find_one({id_name: id}):
            return obj

    @classmethod
    async def update(cls, obj, id: str, id_name: str, collection_name: str):
        """
        :param obj: 업데이트하려는 새 obj
        :param id: collection 에서 업데이트하고싶은 object 의 id
        :param id_name: object 내에서 id 의 필드명 (e.g. uid, rid, pid, ...)
        :param collection_name: 대상 collection 의 이름 (e.g. 'users', 'reviews', 'books'...)
        :return: 업데이트된 obj
        """
        if not obj:
            logger.info(
                f"[MongoDB][{collection_name}]\t object for {collection_name} is null"
            )

        collection = cls.db[collection_name]
        result = await collection.replace_one({id_name: id}, obj.dict())
        if result.modified_count == 1:
            if updated := await collection.find_one({id_name: id}):
                return updated

            if existing := await collection.find_one({id_name: id}):
                return existing

            else:
                return None

    @classmethod
    async def delete(cls, id: str, id_name: str, collection_name: str):
        """
        :param id: collection 에서 삭제하고싶은 object 의 id
        :param id_name: object 내에서 id 의 필드명 (e.g. uid, rid, pid, ...)
        :param collection_name: 대상 collection 의 이름 (e.g. 'users', 'reviews', 'books'...)
        :return: 삭제 결과
        """
        collection = cls.db[collection_name]

        result = await collection.delete_one({id_name: id})

        return True if result.deleted_count == 1 else False
