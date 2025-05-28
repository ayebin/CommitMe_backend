from flask import Blueprint, request, jsonify
from sqlalchemy.sql import exists
from models import db, Session, Message, Sender, Info
from datetime import datetime
#from chatbot import get_response

report_bp = Blueprint('report_bp', __name__)

# @report_bp.route('/comp_report', methods=['POST'])
# def comprehensive_report():
