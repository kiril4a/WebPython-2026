from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required
from flask_mail import Message

from ..admin.routes import admin_required
from ..extensions import mail
from ..forms import MailForm


mail_bp = Blueprint("mail", __name__)


@mail_bp.route("/send", methods=["GET", "POST"])
@login_required
@admin_required
def send_mail():
    form = MailForm()
    if form.validate_on_submit():
        message = Message(subject=form.subject.data, recipients=[form.recipient.data], body=form.body.data)
        try:
            mail.send(message)
            flash("Лист надіслано.")
        except Exception as exc:
            flash(f"Лист не надіслано: {exc}")
        return redirect(url_for("admin.dashboard"))
    return render_template("mail/send.html", form=form)
