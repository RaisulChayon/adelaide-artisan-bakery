import re
from decimal import Decimal, InvalidOperation


CATEGORIES = {
    "Bread",
    "Pastry",
    "Cake",
    "Savoury",
    "Other",
}


def validate_product(name, category, description, price):
    errors = []

    name = name.strip()
    category = category.strip()
    description = description.strip()
    price = price.strip()

    if not name:
        errors.append("Product name is required.")
    elif len(name) > 120:
        errors.append("Product name must be 120 characters or fewer.")

    if not category:
        errors.append("Please select a product category.")
    elif category not in CATEGORIES:
        errors.append("Please select a valid product category.")

    if not description:
        errors.append("Product description is required.")
    elif len(description) > 2000:
        errors.append(
            "Product description must be 2000 characters or fewer."
        )

    try:
        value = Decimal(price)

        if value < 0:
            errors.append("Price cannot be negative.")

        if value.as_tuple().exponent < -2:
            errors.append(
                "Price cannot contain more than two decimal places."
            )

    except (InvalidOperation, ValueError):
        errors.append(
            "Please enter a valid price, for example 6.50."
        )

    return errors


def validate_enquiry(name, email, message):
    errors = []

    name = name.strip()
    email = email.strip()
    message = message.strip()

    if not name:
        errors.append("Name is required.")
    elif len(name) > 120:
        errors.append("Name must be 120 characters or fewer.")

    if not email:
        errors.append("Email address is required.")
    elif len(email) > 255:
        errors.append(
            "Email address must be 255 characters or fewer."
        )
    elif not re.fullmatch(
        r"[^@\s]+@[^@\s]+\.[^@\s]+",
        email,
    ):
        errors.append("Please enter a valid email address.")

    if not message:
        errors.append("Message is required.")
    elif len(message) < 10:
        errors.append(
            "Message must contain at least 10 characters."
        )
    elif len(message) > 2000:
        errors.append(
            "Message must be 2000 characters or fewer."
        )

    return errors