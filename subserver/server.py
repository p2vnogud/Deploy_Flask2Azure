from myapp import create_app
from myapp.database import db, Message, ChatMessage
from flask_socketio import emit, join_room, leave_room

app, socket = create_app()

# COMMUNICATION ARCHITECTURE

# Join-chat event. Emit online message to other users and join the room
@socket.on("join-chat")
def join_private_chat(data):
    room = data.get("rid")
    if not room:
        emit("error", {"msg": "Room ID is required"})
        return

    join_room(room=room)
    socket.emit(
        "joined-chat",
        {"msg": f"{room} is now online."},
        room=room,
    )


@socket.on("invite")
def hwhw(data):
    to_id = data.get("rid")
    from_id = data.get("from")
    content = data.get("content")

    if not (to_id and from_id and content):
        emit("error", {"msg": "Invalid invite data"})
        return

    invite_data = {"from": from_id, "to": to_id, "content": content}
    socket.emit("invited", invite_data)


@socket.on("noti-chat")
def noti_chat(data):
    socket.emit("receive-notichat", data)


@socket.on("gen_user")
def gengen(data):
    chatroom = data.get("room_id")
    user_id = data.get("to_id")
    
    if not (chatroom and user_id):
        emit("error", {"msg": "Invalid data for gen_user"})
        return

    response = [chatroom, user_id]
    socket.emit("gengen", response)


# Outgoing event handler
@socket.on("outgoing")
def chatting_event(json):
    """
    Handles saving messages and sending messages to all clients.
    """
    room_id = json.get("rid")
    timestamp = json.get("timestamp")
    message = json.get("message")
    sender_id = json.get("sender_id")
    sender_username = json.get("sender_username")

    if not (room_id and timestamp and message and sender_id and sender_username):
        emit("error", {"msg": "Invalid message data"})
        return

    # Ensure the room entry exists
    message_entry = Message.query.filter_by(room_id=room_id).first()
    if not message_entry:
        message_entry = Message(room_id=room_id)
        try:
            db.session.add(message_entry)
            db.session.commit()
        except Exception as e:
            print(f"Error creating room: {e}")
            db.session.rollback()
            emit("error", {"msg": "Database error while creating room"})
            return

    # Create the chat message
    chat_message = ChatMessage(
        content=message,
        timestamp=timestamp,
        sender_id=sender_id,
        sender_username=sender_username,
        room_id=room_id,
    )

    try:
        # Save the new chat message
        db.session.add(chat_message)
        db.session.commit()
    except Exception as e:
        print(f"Error saving message to the database: {e}")
        db.session.rollback()
        emit("error", {"msg": "Database error while saving message"})
        return

    # Emit the message to other users in the room
    socket.emit(
        "message",
        json,
        room=room_id,
        include_self=False,
    )


if __name__ == "__main__":
    socket.run(app, allow_unsafe_werkzeug=True, debug=True, port=7777)
