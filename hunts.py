"""
This is the people module and supports all the REST actions for the
people data
"""

from flask import make_response, abort
from config import db
from models import Person, Hunt, HuntSchema, Question


def read_all():
    """
    This function responds to a request for /api/hunts
    with the complete list of hunts, sorted by hunt timestamp

    :return:                json list of all hunts
    """
    # Query the database for all the notes
    hunts = Hunt.query.order_by(db.desc(Hunt.timestamp)).all()

    # Serialize the list of hunts from our data
    hunt_schema = HuntSchema(many=True)
    data = hunt_schema.dump(hunts).data
    return data


def read_one(hunt_id):
    """
    This function responds to a request for
    /api/hunt/{hunt_id}
    with one matching note for the associated person

    :param hunt_id:         Id of hunt
    :return:                json string of hunt contents
    """
    # Query the database for the hunt
    hunt = (
        Hunt.query.filter(Hunt.hunt_id == hunt_id)
        .outerjoin(Question)
        .one_or_none()
    )

    # Was a hunt found?
    if hunt is not None:
        hunt_schema = HuntSchema()
        data = hunt_schema.dump(hunt).data
        return data

    # Otherwise, nope, didn't find that note
    else:
        abort(404, f"Hunt not found for Id: {hunt_id}")


def create(person_id, hunt):
    """
    This function creates a new hunt related to the creator passed in person id.

    :param person_id:       Id of the person who created the hunt
    :param hunt:            The JSON containing the hunt data
    :return:                201 on success
    """
    # get the parent person
    person = Person.query.filter(Person.person_id == person_id).one_or_none()

    # Was a person found?
    if person is None:
        abort(404, f"Person not found for Id: {person_id}")

    # Create a hunt schema instance
    schema = HuntSchema()
    new_hunt = schema.load(hunt, session=db.session).data

    # Add the note to the person and database
    person.hunts.append(new_hunt)
    db.session.commit()

    # Serialize and return the newly created note in the response
    data = schema.dump(hunt).data

    return data, 201


def update(person_id, hunt_id, hunt):
    """
    This function updates an existing hunt related to the passed in
    person id.

    :param person_id:       Id of the person the hunt is related to
    :param hunt_id:         Id of the hunt to update
    :param hunt:            The JSON containing the hunt data
    :return:                200 on success
    """
    update_hunt = (
        Hunt.query.filter(Person.person_id == person_id)
        .filter(Hunt.hunt_id == hunt_id)
        .one_or_none()
    )

    # Did we find an existing note?
    if update_hunt is not None:

        # turn the passed in note into a db object
        schema = HuntSchema()
        update = schema.load(hunt, session=db.session).data

        # Set the id's to the note we want to update
        update.person_id = update_hunt.person_id
        update.hunt_id = update_hunt.hunt_id

        # merge the new object into the old and commit it to the db
        db.session.merge(update)
        db.session.commit()

        # return updated note in the response
        data = schema.dump(update_hunt).data

        return data, 200

    # Otherwise, nope, didn't find that note
    else:
        abort(404, f"Hunt not found for Id: {hunt_id}")


def delete(person_id, hunt_id):
    """
    This function deletes a hunt

    :param person_id:   Id of the person the hunt is related to
    :param hunt_id:     Id of the hunt to delete
    :return:            200 on successful delete, 404 if not found
    """
    # Get the note requested
    hunt = (
        Hunt.query.filter(Hunt.hunt_id == hunt_id)
        .filter(Hunt.creator == person_id)
        .one_or_none()
    )

    # did we find a hunt?
    if hunt is not None:
        db.session.delete(hunt)
        db.session.commit()
        return make_response(
            "Hunt {hunt_id} deleted".format(hunt_id=hunt_id), 200
        )

    # Otherwise, nope, didn't find that note
    else:
        abort(404, f"Hunt not found for Id: {hunt_id}")
