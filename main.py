import json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.config import Configuration
from app.forms.classification_form import ClassificationForm
from app.forms.transformation_form import TransformationForm
from app.ml.classification_utils import classify_image
from app.utils import list_images
from app.ml.transformation_utils import transform_image


app = FastAPI()
config = Configuration()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/info")
def info() -> dict[str, list[str]]:
    """Returns a dictionary with the list of models and
    the list of available image files."""
    list_of_images = list_images()
    list_of_models = Configuration.models
    data = {"models": list_of_models, "images": list_of_images}
    return data


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    """The home page of the service."""
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/classifications")
def create_classify(request: Request):
    return templates.TemplateResponse(
        "classification_select.html",
        {"request": request, "images": list_images(), "models": Configuration.models},
    )


@app.post("/classifications")
async def request_classification(request: Request):
    form = ClassificationForm(request)
    await form.load_data()
    image_id = form.image_id
    model_id = form.model_id
    classification_scores = classify_image(model_id=model_id, img_id=image_id)
    return templates.TemplateResponse(
        "classification_output.html",
        {
            "request": request,
            "image_id": image_id,
            "classification_scores": json.dumps(classification_scores),
        },
    )

@app.get("/image-transformation")
def create_transform(request: Request):
    return templates.TemplateResponse(
        "image_transformation_select.html",
        {"request": request, "images": list_images()},
    )

@app.post("/image-transformation")
async def request_transformation(request: Request):
    form = TransformationForm(request)
    await form.load_data()
    image_id = form.image_id
    color = form.color
    brightness = form.brightness
    contrast = form.contrast
    sharpness = form.sharpness

    #show types of the transformation values
    print(type(color))
    print(type(brightness))
    print(type(contrast))
    print(type(sharpness))

    # print the transformation values
    print(color)
    print(brightness)
    print(contrast)
    print(sharpness)
    
    transformed_image = transform_image(
        image_id=image_id,
        color=color,
        brightness=brightness,
        contrast=contrast,
        sharpness=sharpness,
    )
    #show the transformed image (for debugging)
    transformed_image.show()
    return templates.TemplateResponse(
        "image_transformation_output.html",
        {
            "request": request,
            "image_id": image_id,
        },
    )