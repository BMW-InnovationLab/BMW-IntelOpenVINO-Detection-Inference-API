import sys
from typing import List
from models import ApiResponse
from inference.errors import Error
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from deep_learning_service import DeepLearningService
from fastapi import FastAPI, Form, File, UploadFile, Header
from inference.exceptions import ModelNotFound, InvalidModelConfiguration, ApplicationError, ModelNotLoaded, \
	InferenceEngineNotFound, InvalidInputData
from __version__ import __version__

sys.path.append('./inference')

dl_service = DeepLearningService()
error_logging = Error()
app = FastAPI(version=__version__, title='BMW InnovationLab OpenVINO Inference Automation',
			  description="<b>API for performing OpenVINO inference</b>")


@app.get('/load')
def load_custom():
	"""
	Loads all the available models.
	:return: All the available models with their respective hashed values
	"""
	try:
		return dl_service.load_all_models()
	except ApplicationError as e:
		return ApiResponse(success=False, error=e)
	except Exception:
		return ApiResponse(success=False, error='unexpected server error')


@app.post('/detect')
async def detect_custom(model: str = Form(...), image: UploadFile = File(...)):
	"""
	Performs a prediction for a specified image using one of the available models.
	:param model: Model name or model hash
	:param image: Image file
	:return: Model's Bounding boxes
	"""
	draw_boxes = False
	try:
		output = await dl_service.run_model(model, image, draw_boxes)
		error_logging.info('request successful;' + str(output))
		return output
	except ApplicationError as e:
		error_logging.warning(model + ';' + str(e))
		return ApiResponse(success=False, error=e)
	except Exception as e:
		error_logging.error(model + ' ' + str(e))
		return ApiResponse(success=False, error='unexpected server error')


@app.post('/models/{model_name}/predict_image')
async def predict_image(model_name: str, input_data: UploadFile = File(...)):
	"""
	Draws bounding box(es) on image and returns it.
	:param model_name: Model name
	:param input_data: Image file
	:return: Image file
	"""
	try:
		output = await dl_service.run_model(model_name, input_data, draw=True)
		error_logging.info('request successful;' + str(output))
		return FileResponse("/app/result.jpg", media_type="image/jpg")
	except ApplicationError as e:
		error_logging.warning(model_name + ';' + str(e))
		return ApiResponse(success=False, error=e)
	except Exception as e:
		error_logging.error(model_name + ' ' + str(e))
		return ApiResponse(success=False, error='unexpected server error')