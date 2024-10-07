from typing import Type

import pydantic
from flask import Flask, jsonify, request
from flask.views import MethodView

from models import Session, Advertisements
from errors import HttpError, PatchAdvt

app = Flask("app")


def validate(errors: Type[PatchAdvt], json_data: dict):
    try:
        model = errors(**json_data)
        validate_data = model.dict(exclude_none=True)
    except pydantic.ValidationError as er:
        raise HttpError(400, er.errors())
    return validate_data


@app.errorhandler(HttpError)
def http_error_handler(err: HttpError):
    response = jsonify(
        {
            "status": "error",
            "message": err.message,
        }
    )
    response.status_code = err.status_sode
    return response


def get_adv(adv_id, session):
    adv = session.query(Advertisements).get(adv_id)
    if adv is None:
        raise HttpError(404, "Не найдено")
    return adv


class AdsViews(MethodView):
    def get(self, adv_id: int):
        with Session() as session:
            adv = get_adv(adv_id, session)
            return jsonify(
                {
                    "id": adv.id,
                    "author": adv.author,
                    "title": adv.title,
                    "description": adv.description,
                    "creation_time": adv.creation_time.isoformat(),
                }
            )

    def patch(self, adv_id: int):
        json_data = validate(PatchAdvt, request.json)
        with Session() as session:
            adv = get_adv(adv_id, session)
            for k, v in json_data.items():
                setattr(adv, k, v)
                session.add(adv)
                session.commit()
            return jsonify(
                {
                    "id": adv.id,
                    "author": adv.author,
                    "title": adv.title,
                    "description": adv.description,
                    "creation_time": adv.creation_time.isoformat(),
                }
            )

    def delete(self, adv_id: int):
        with Session() as session:
            adv = get_adv(adv_id, session)
            session.delete(adv)
            session.commit()
        return jsonify(
            {
                "id": adv.id,
                "status": "Deleted",
            }
        )

    def post(self):
        json_data = dict(request.json)
        with Session() as session:
            new_ad = Advertisements(**json_data)
            session.add(new_ad)
            session.commit()
            return jsonify(
                {
                    "id": new_ad.id,
                    "author": new_ad.author,
                    "title": new_ad.title,
                    "description": new_ad.description,
                    "creation_time": new_ad.creation_time.isoformat(),
                }
            )


app.add_url_rule("/adv/", methods=["POST"], view_func=AdsViews.as_view("create_adv"))
app.add_url_rule(
    "/adv/<int:adv_id>",
    methods=["GET", "PATCH", "DELETE"],
    view_func=AdsViews.as_view("get_adv"),
)
if __name__ == "__main__":
    app.run()
