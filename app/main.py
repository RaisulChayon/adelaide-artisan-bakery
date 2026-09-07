from decimal import Decimal

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette.status import HTTP_303_SEE_OTHER
from starlette.templating import Jinja2Templates

from .database import Base, engine, get_db
from .models import Enquiry, Product
from .validation import validate_enquiry, validate_product


app = FastAPI(
    title="Adelaide Artisan Bakery",
    description="Bakery catalogue and customer enquiry website",
    version="1.0.0",
)

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static",
)

templates = Jinja2Templates(directory="templates")

Base.metadata.create_all(bind=engine)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = (
        "strict-origin-when-cross-origin"
    )

    return response


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return templates.TemplateResponse(
        request=request,
        name="404.html",
        context={
            "request": request,
        },
        status_code=404,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc):
    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={
            "request": request,
            "title": "Invalid request",
            "message": (
                "The request could not be processed. "
                "Please check the information and try again."
            ),
        },
        status_code=422,
    )


@app.get("/", response_class=HTMLResponse)
def home(
    request: Request,
    db: Session = Depends(get_db),
):
    products = (
        db.query(Product)
        .filter(Product.available.is_(True))
        .order_by(Product.category, Product.name)
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
            "products": products,
        },
    )


@app.get("/products", response_class=HTMLResponse)
def products(
    request: Request,
    db: Session = Depends(get_db),
):
    products = (
        db.query(Product)
        .order_by(Product.id.desc())
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="products.html",
        context={
            "request": request,
            "products": products,
            "message": request.query_params.get("message"),
        },
    )


@app.get("/products/new", response_class=HTMLResponse)
def new_product(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="product_form.html",
        context={
            "request": request,
            "product": None,
            "action": "Create",
            "errors": [],
        },
    )


@app.post("/products/new")
def create_product(
    request: Request,
    name: str = Form(""),
    category: str = Form(""),
    description: str = Form(""),
    price: str = Form(""),
    available: bool = Form(False),
    db: Session = Depends(get_db),
):
    errors = validate_product(
        name,
        category,
        description,
        price,
    )

    if errors:
        return templates.TemplateResponse(
            request=request,
            name="product_form.html",
            context={
                "request": request,
                "product": {
                    "name": name,
                    "category": category,
                    "description": description,
                    "price": price,
                    "available": available,
                },
                "action": "Create",
                "errors": errors,
            },
            status_code=422,
        )

    product = Product(
        name=name.strip(),
        category=category.strip(),
        description=description.strip(),
        price=Decimal(price.strip()),
        available=available,
    )

    try:
        db.add(product)
        db.commit()
    except SQLAlchemyError:
        db.rollback()

        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={
                "request": request,
                "title": "Unable to save product",
                "message": (
                    "The product could not be saved. "
                    "Please try again."
                ),
            },
            status_code=500,
        )

    return RedirectResponse(
        "/products?message=Product+created+successfully.",
        status_code=HTTP_303_SEE_OTHER,
    )


@app.get(
    "/products/{product_id}/edit",
    response_class=HTMLResponse,
)
def edit_product(
    request: Request,
    product_id: int,
    db: Session = Depends(get_db),
):
    product = db.get(Product, product_id)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    return templates.TemplateResponse(
        request=request,
        name="product_form.html",
        context={
            "request": request,
            "product": product,
            "action": "Update",
            "errors": [],
        },
    )


@app.post("/products/{product_id}/edit")
def update_product(
    request: Request,
    product_id: int,
    name: str = Form(""),
    category: str = Form(""),
    description: str = Form(""),
    price: str = Form(""),
    available: bool = Form(False),
    db: Session = Depends(get_db),
):
    product = db.get(Product, product_id)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    errors = validate_product(
        name,
        category,
        description,
        price,
    )

    if errors:
        return templates.TemplateResponse(
            request=request,
            name="product_form.html",
            context={
                "request": request,
                "product": {
                    "id": product_id,
                    "name": name,
                    "category": category,
                    "description": description,
                    "price": price,
                    "available": available,
                },
                "action": "Update",
                "errors": errors,
            },
            status_code=422,
        )

    product.name = name.strip()
    product.category = category.strip()
    product.description = description.strip()
    product.price = Decimal(price.strip())
    product.available = available

    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()

        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={
                "request": request,
                "title": "Unable to update product",
                "message": (
                    "The product could not be updated. "
                    "Please try again."
                ),
            },
            status_code=500,
        )

    return RedirectResponse(
        "/products?message=Product+updated+successfully.",
        status_code=HTTP_303_SEE_OTHER,
    )


@app.post("/products/{product_id}/delete")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    product = db.get(Product, product_id)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    try:
        db.delete(product)
        db.commit()
    except SQLAlchemyError:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="The product could not be deleted.",
        )

    return RedirectResponse(
        "/products?message=Product+deleted+successfully.",
        status_code=HTTP_303_SEE_OTHER,
    )


@app.get(
    "/enquiry",
    response_class=HTMLResponse,
)
def enquiry_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="enquiry.html",
        context={
            "request": request,
            "errors": [],
            "values": {},
        },
    )


@app.post("/enquiry")
def submit_enquiry(
    request: Request,
    name: str = Form(""),
    email: str = Form(""),
    message: str = Form(""),
    db: Session = Depends(get_db),
):
    errors = validate_enquiry(
        name,
        email,
        message,
    )

    if errors:
        return templates.TemplateResponse(
            request=request,
            name="enquiry.html",
            context={
                "request": request,
                "errors": errors,
                "values": {
                    "name": name,
                    "email": email,
                    "message": message,
                },
            },
            status_code=422,
        )

    enquiry = Enquiry(
        name=name.strip(),
        email=email.strip(),
        message=message.strip(),
    )

    try:
        db.add(enquiry)
        db.commit()
    except SQLAlchemyError:
        db.rollback()

        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={
                "request": request,
                "title": "Unable to submit enquiry",
                "message": (
                    "Your enquiry could not be stored. "
                    "Please try again."
                ),
            },
            status_code=500,
        )

    return RedirectResponse(
        "/enquiry?success=1",
        status_code=HTTP_303_SEE_OTHER,
    )


@app.get(
    "/enquiries",
    response_class=HTMLResponse,
)
def enquiries(
    request: Request,
    db: Session = Depends(get_db),
):
    enquiries = (
        db.query(Enquiry)
        .order_by(Enquiry.id.desc())
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="enquiries.html",
        context={
            "request": request,
            "enquiries": enquiries,
        },
    )


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "adelaide-artisan-bakery",
    }