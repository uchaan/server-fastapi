"""
앱 내 SNS 게시물 데이터와 관련하여 MongoDB에 접근하는 CRUD 인터페이스  
"""

from loguru import logger

from app.db.crud.crud import Crud
from app.db.models.post import Post


class PostCrud(Crud):
    @staticmethod
    def put_id(p: Post):
        p.pid = p.date.strftime("%Y%m%d%H%M%S") + p.posterUid
        return p

    @classmethod
    async def add(cls, p: Post, collection_name: str):
        p = PostCrud.put_id(p)
        return await super().add(p, collection_name)

    @classmethod
    async def get_multiple(cls, collection_name: str, group="all", last_pid=None):
        """
        group = "student" or "tutor" or "all" (default)
        date 순으로 정렬된 리스트에서 last_pid 뒤의 10개 post를 반환함.
        showtype
        0: 모두 공개 포스트
        1: 아이들만 공개
        2: 튜터들만 공개.
        """

        collection = cls.db[collection_name]

        if group == "all":  # show all posts (showtype = 0,1,2)
            query = {}
        elif group == "student":  # show students' posts (showtype = 0, 1)
            query = {"$or": [{"showType": {"$eq": 0}}, {"showType": {"$eq": 1}}]}
        elif group == "tutor":  # show tutor's posts (showtype = 0, 2)
            query = {"$or": [{"showType": {"$eq": 0}}, {"showType": {"$eq": 2}}]}
        else:
            raise ValueError("param group should be one of (all, student, tutor). ")

        posts = await collection.find(query).sort("date").to_list(None)
        if not last_pid:  # first request
            return posts[:10]

        result_posts = []
        count = 0
        start_flag = 0
        for i, post in enumerate(posts):
            if count == 10:
                return result_posts
            if post["pid"] == last_pid:
                start_flag = 1

            if start_flag:
                count += 1
                result_posts.append(post)

        return result_posts

    @classmethod
    async def update_multiple(cls, uid: str, img_url: str, collection_name: str):
        """
        change img url of all {poster}'s posts, if poster's profile img changed.
        """

        collection = cls.db[collection_name]

        # find all posts from DB.
        posts = await collection.find({"posterUid": uid}).to_list(None)

        # update all img urls
        for post in posts:

            logger.info(post["pid"])
            result = await collection.update_one(
                {"pid": post["pid"]}, {"$set": {"posterImg": img_url}}
            )
            logger.info(f"updating result: {result.modified_count}")

        return
