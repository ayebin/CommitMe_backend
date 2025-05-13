from flask import Blueprint, request, jsonify
from sqlalchemy.sql import exists
from models import db, Session, Message, Sender, Info
from datetime import datetime

chat_bp = Blueprint('chat_bp', __name__)