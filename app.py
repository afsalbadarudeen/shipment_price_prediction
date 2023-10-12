from fastapi import FastAPI, Request
from typing import Optional
from uvicorn import run as app_run
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from shipment.utils.main_utils import MainUtils

#from shipment.components.model_predictor import CostPredictor, shippingData
from shipment.constant import APP_HOST, APP_PORT
#from shipment.pipeline.training_pipeline import TrainPipeline

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DataForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.artist: Optional[str] = None
        self.height: Optional[str] = None
        self.width: Optional[str] = None
        self.weight: Optional[str] = None
        self.material: Optional[str] = None
        self.priceOfSculpture: Optional[str] = None
        self.baseShippingPrice: Optional[str] = None
        self.international: Optional[str] = None
        self.expressShipment: Optional[str] = None
        self.installationIncluded: Optional[str] = None
        self.transport: Optional[str] = None
        self.fragile: Optional[str] = None
        self.customerInformation: Optional[str] = None
        self.remoteLocation: Optional[str] = None

    async def get_shipping_data(self):
        form = await self.request.form()
        self.artist = form.get("artist")
        self.height = form.get("height")
        self.width = form.get("width")
        self.weight = form.get("weight")
        self.material = form.get("material")
        self.priceOfSculpture = form.get("priceOfSculpture")
        self.baseShippingPrice = form.get("baseShippingPrice")
        self.international = form.get("international")
        self.expressShipment = form.get("expressShipment")
        self.installationIncluded = form.get("installationIncluded")
        self.transport = form.get("transport")
        self.fragile = form.get("fragile")
        self.customerInformation = form.get("customerInformation")
        self.remoteLocation = form.get("remoteLocation")


@app.get("/train")
async def trainRouteClient():
    try:
        train_pipeline = TrainPipeline()

        train_pipeline.run_pipeline()

        return Response("Training successful !!")

    except Exception as e:
        return Response(f"Error Occurred! {e}")


@app.get("/predict")
async def predictGetRouteClient(request: Request):
    try:

        return templates.TemplateResponse(
            "index.html",
            {"request": request, "context": "Rendering"},
        )

    except Exception as e:
        return Response(f"Error Occurred! {e}")


@app.post("/predict")
async def predictRouteClient(request: Request):
    try:

        form = DataForm(request)
        await form.get_shipping_data()

        shipping_data = shippingData(
            artist=form.artist,
            height=form.height,
            width=form.width,
            weight=form.weight,
            material=form.material,
            priceOfSculpture=form.priceOfSculpture,
            baseShippingPrice=form.baseShippingPrice,
            international=form.international,
            expressShipment=form.expressShipment,
            installationIncluded=form.installationIncluded,
            transport=form.transport,
            fragile=form.fragile,
            customerInformation=form.customerInformation,
            remoteLocation=form.remoteLocation,
        )

        cost_df = shipping_data.get_input_data_frame()
        cost_predictor = CostPredictor()
        cost_value = round(cost_predictor.predict(X=cost_df)[0], 2)

        return templates.TemplateResponse(
            "index.html",
            {"request": request, "context": cost_value},
        )


    except Exception as e:
        return {"status": False, "error": f"{e}"}


if __name__ == "__main__":
    app_run(app, host=APP_HOST, port=APP_PORT)