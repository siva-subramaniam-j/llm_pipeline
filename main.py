from fastapi import FastAPI, UploadFile, File, HTTPException
import shutil
from tempfile import NamedTemporaryFile
from document_ingest_pipeline import preprocessing_pipeline
from rag_pipeline import rag_pipeline
import uvicorn
from pydantic import BaseModel

app = FastAPI()

@app.post("/uploadfile")
async def upload_file(file: UploadFile = File(...)):
    print("hitting endpoint")
    print(file.content_type)
    if file.content_type not in  ["application/octet-stream","text/plain" , "application/pdf" , "text/markdown"]:
        raise HTTPException(status_code=400, detail="Only text files are supported.")

    print("supported file")
    file_extension = file.filename.split('.')[-1]
    suffix = f".{file_extension}"
    
    # Save the uploaded file to a temporary location with the original extension
    with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    # Run the Haystack pipeline
    try:
        print("going to run pipeline")
        preprocessing_pipeline.run({"file_type_router": {"sources": [tmp_path]}})
    except Exception as e:
        print(e)
        print("some error happened")
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": "File processed successfully"}

class QueryRequest(BaseModel):
    query: str

@app.post("/query")
async def rag_query(request: QueryRequest):
    print(request.query)
    
    try:
        print("going to run the pipeline")
        result=rag_pipeline.run(
    {
        "embedder": {"text": request.query},
        "prompt_builder": {"question": request.query},
        
    }
)   
        return(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



if __name__=="__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
    