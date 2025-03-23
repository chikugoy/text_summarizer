from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
import uuid

from app.database import get_db
from app.models import Summary, Image
from app.schemas import SummaryCreate, SummaryUpdate, SummaryBase, SummaryDetail, SummaryList
from app.services import summary_service

router = APIRouter()


@router.post("", response_model=SummaryDetail, status_code=status.HTTP_201_CREATED)
def create_summary(
    summary: SummaryCreate,
    db: Session = Depends(get_db)
):
    """OCR処理された文章から要約を生成して保存する"""
    # 要約の作成
    db_summary = Summary(
        title=summary.title,
        description=summary.description,
        original_text=summary.original_text,
        summarized_text=summary.summarized_text
    )
    
    db.add(db_summary)
    db.commit()
    db.refresh(db_summary)
    
    return db_summary


@router.post("/generate", response_model=SummaryDetail)
def generate_summary(
    summary_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """特定の要約IDに関連する画像からOCRテキストを抽出し、要約を生成する"""
    # 要約の存在確認
    summary = db.query(Summary).filter(Summary.id == summary_id).first()
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID {summary_id} の要約が見つかりません"
        )
    
    # 関連する画像の取得
    images = db.query(Image).filter(Image.summary_id == summary_id).order_by(Image.page_number).all()
    if not images:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="この要約に関連する画像がありません"
        )
    
    # OCRテキストの結合
    original_text = ""
    for image in images:
        if image.ocr_text:
            original_text += image.ocr_text + "\n\n"
    
    if not original_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OCRテキストが抽出されていません。先にOCR処理を実行してください。"
        )
    
    # 要約の生成
    summarized_text = summary_service.summarize_text(original_text)
    
    # 要約の更新
    summary.original_text = original_text
    summary.summarized_text = summarized_text
    
    db.commit()
    db.refresh(summary)
    
    return summary


@router.get("", response_model=SummaryList)
def get_summaries(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """要約一覧を取得する（ページネーション付き）"""
    total = db.query(Summary).count()
    summaries = db.query(Summary).order_by(Summary.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "items": summaries,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "page_size": limit
    }


@router.get("/{summary_id}", response_model=SummaryDetail)
def get_summary(
    summary_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """特定の要約詳細を取得する"""
    summary = db.query(Summary).filter(Summary.id == summary_id).first()
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID {summary_id} の要約が見つかりません"
        )
    
    return summary


@router.put("/{summary_id}", response_model=SummaryDetail)
def update_summary(
    summary_id: uuid.UUID,
    summary_update: SummaryUpdate,
    db: Session = Depends(get_db)
):
    """既存の要約情報を更新する（タイトル、説明など）"""
    summary = db.query(Summary).filter(Summary.id == summary_id).first()
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID {summary_id} の要約が見つかりません"
        )
    
    # 更新するフィールドを設定
    if summary_update.title is not None:
        summary.title = summary_update.title
    if summary_update.description is not None:
        summary.description = summary_update.description
    
    db.commit()
    db.refresh(summary)
    
    return summary


@router.delete("/{summary_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_summary(
    summary_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """要約を削除する"""
    summary = db.query(Summary).filter(Summary.id == summary_id).first()
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID {summary_id} の要約が見つかりません"
        )
    
    # 関連する画像も削除される（cascade="all, delete-orphan"の設定による）
    db.delete(summary)
    db.commit()
    
    return None
