import bcrypt
from aiohttp_apispec import docs, request_schema, response_schema, querystring_schema
from sqlalchemy.orm import session

from app.crm.schemes import AddTopicSchema, AddJokeSchema, ListTopicSchema, GetJokeRequestSchema, \
    GetJokeResponseSchema, UserRegisterSchema, UserLoginSchema, ListGetUserResponse, JokeUpdateSchema, RatingJokeSchema
from app.web.app import View
from app.crm.model import Jokes, Topic,User
from app.web.schemes import OkResponseSchema
from app.web.utils import json_response

class AddNewUserView(View):
    @docs(tags=['Users'],
          summary="Add New User",
          description="Add a new user")
    @request_schema(UserRegisterSchema)
    @response_schema(OkResponseSchema)
    async def post(self):
        data = self.request['data']
        user = await self.request.app.crm_accessor.register_user(**data)
        return json_response(
            status="ok, hello",
            data={
                "mail": user.mail
            }
        )
class LoginView(View):
    @docs(tags=['Users'],
          summary="Login",
          description="Login")
    @request_schema(UserLoginSchema)
    @response_schema(OkResponseSchema)
    async def post(self):
        data = self.request['data']
        token = await self.request.app.crm_accessor.login_user(**data)
        return json_response(
            status="success",
            data={
                "message": "your authorization successful",
                "token": token
            }
        )


class AddNewTopicView(View):
    @docs(tags=["Topics"],
          summary="Add a new topic",
          description="Add a new topic to database",
          security=[{"BearerAuth": []}])
    @request_schema(AddTopicSchema)
    @response_schema(OkResponseSchema)
    async def post(self):
        data = self.request["data"]


        topic = await self.request.app.crm_accessor.add_topic(**data)
        return json_response(data={
            "id": topic.topic_id,
            "title": topic.title,
            "count": topic.count,
        })

class AddNewJokeView(View):
    @docs(tags=["Jokes"],
          summary="Add a new joke",
          description="Add a new joke to database",
          security=[{"BearerAuth": []}])
    @request_schema(AddJokeSchema)
    @response_schema(OkResponseSchema)
    async def post(self):
        data = self.request["data"]

        joke = await self.request.app.crm_accessor.add_joke(**data)
        return json_response(data={
            "id": joke.joke_id,
            "text": joke.text,
            "topic_id": joke.topic_id,
        })

class ListAllTopicView(View):
    @docs(tags=["Topics"],
          summary="Get all topics",
          description="Get all topics from database")
    @response_schema(ListTopicSchema, 200)
    async def get(self):
        topics = await self.request.app.crm_accessor.list_topics()
        return json_response(data=[{
            "id": topic.topic_id,
            "title": topic.title,
            "count": topic.count,
        }
        for topic in topics])

class DeleteJokeView(View):
    @docs(tags=["Jokes"],
          summary="Delete a joke",
          description="Delete a joke from database",
          security=[{"BearerAuth": []}])
    async def delete(self):
        joke_id = int(self.request.match_info["joke_id"]) #берём из урла
        deleted = await self.request.app.crm_accessor.delete_joke(joke_id = joke_id)
        if not deleted:
            return json_response(status="error", data={"message": "joke not found"})
        return json_response(data={"message": "joke deleted" }, status="success")

class GetJokeView(View):
    @docs(tags=["Jokes"],
          summary="Get a joke",
          description="Get a joke from database")
    @querystring_schema(GetJokeRequestSchema)
    @response_schema(GetJokeResponseSchema)
    async def get(self):
        text = self.request.query.get("text")
        joke = await self.request.app.crm_accessor.get_joke_by_title(text = text)
        return json_response(
            data=[{
                "text": j.text,
            }for j in joke])

class GetUsersView(View):
    @docs(tags=["Users"],
          summary="Get all users",
          description="Get all users from database",
          security=[{"BearerAuth": []}])
    @response_schema(ListGetUserResponse)
    async def get(self):
        user = await self.request.app.crm_accessor.get_user()
        return json_response(data=[{
            "id": users.user_id,
            "name": users.name,
            "mail": users.mail,
        } for users in user])

class UpdateJokeView(View):
    @docs(tags=["Jokes"],
          summary="Update a joke",
          description="Update a joke from database",
          security=[{"BearerAuth": []}])
    @request_schema(JokeUpdateSchema)
    @response_schema(GetJokeResponseSchema)
    async def put(self):
        joke_id = int(self.request.match_info["joke_id"])
        data = self.request["data"]

        joke = await self.request.app.crm_accessor.joke_update(joke_id = joke_id, **data)
        return json_response(
            status = "updated",
            data={
                "id": joke.joke_id,
                "text": joke.text,
                "topic_id": joke.topic_id,
            })

class DeleteTopicsView(View):
    @docs(tags=["Topics"],
          summary="Delete all topics",
          description="Delete all topics from database",
          security=[{"BearerAuth": []}])
    async def delete(self):
        topic_id = int(self.request.match_info["topic_id"])
        deleted = await self.request.app.crm_accessor.delete_topic(topic_id = topic_id)
        if not deleted:
            return json_response(status="error", data={"message": "topic not found"})
        return json_response( data = {
            "message": "topic deleted" },
            status = "success deleted")


class RateJokeView(View):
    @docs(tags=["Jokes"],
          summary="Rate a joke",
          description="Rate a joke from database",
          security=[{"BearerAuth": []}])
    @request_schema(RatingJokeSchema)
    async def put(self):
        joke_id = int(self.request.match_info["joke_id"])
        data = self.request["data"]

        user_id = self.request["user_id"]

        rating = await self.request.app.crm_accessor.rate_joke(joke_id, user_id, data["value"])
        if not rating:
            return json_response(status="error", data={"message": "joke not found"})

        return json_response(data = {
            "joke_id": joke_id,
            "user_id": user_id,
            "value": rating.value
        },
            status = "success")

