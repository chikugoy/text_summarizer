from app.schemas.summary import (
    SummaryBase, SummaryCreate, SummaryUpdate,
    SummaryDetail, SummaryList, SummaryGenerate
)
from app.schemas.image import (
    ImageBase, ImageCreate, ImageDetail, ImageList,
    OCRRequest, OCRResult, OCRResponse
)

# スキーマをここにインポートすることで、他のモジュールから簡単にインポートできるようになります
# 例: from app.schemas import SummaryCreate, ImageDetail
