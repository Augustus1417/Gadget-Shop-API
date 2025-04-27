from .. import schemas, models
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter, Response
from ..database import get_db

router = APIRouter()

@router.get('/', response_model=list[schemas.ProductBaseSchema])
def get_products(db: Session=Depends(get_db)):
    products = db.query(models.Products).all()
    return products

@router.get('/phones', response_model=list[schemas.ProductBaseSchema])
def get_phones(db: Session=Depends(get_db)):
    phones = db.query(models.Products).filter(models.Products.category == "phone").all()
    return phones

@router.get('/laptops', response_model=list[schemas.ProductBaseSchema])
def get_laptops(db: Session=Depends(get_db)):
    laptops = db.query(models.Products).filter(models.Products.category == "laptop").all()
    return laptops

@router.get('/accessories', response_model=list[schemas.ProductBaseSchema])
def get_accessories(db: Session=Depends(get_db)):
    accessories = db.query(models.Products).filter(models.Products.category == "accessory").all()
    return accessories

@router.get('/get/{product_id}', response_model=schemas.ProductBaseSchema)
def get_product_by_id(product_id: int, db: Session=Depends(get_db)):
    product = db.query(models.Products).filter(models.Products.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product

@router.post('/', response_model=schemas.ProductBaseSchema, status_code=status.HTTP_201_CREATED)
def create_product(payload: schemas.NewProduct, db: Session=Depends(get_db)):
    new_product = models.Products(**payload.model_dump())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@router.delete('/delete/{product_id}')
def delete_product(product_id: int, db: Session=Depends(get_db)):
    product_query = db.query(models.Products).filter(models.Products.product_id == product_id)
    product = product_query.first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    product_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)