from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import Model

API_KEY = "F62rCiGk_WqjNh1hA0rYWVk7sM799zvEXtUMruDu5Z6R"
PROJECT_ID = "34586bb6-05a3-4243-87e6-7512e1ec169b"

credentials = Credentials(
    url="https://eu-de.ml.cloud.ibm.com",
    api_key=API_KEY
)

model = Model(
    model_id="ibm/granite-4-h-small",
    credentials=credentials,
    project_id=PROJECT_ID
)

print(model.generate_text("Hello"))