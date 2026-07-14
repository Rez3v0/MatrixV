import boto3
from botocore.client import Config
import logging
from backend.config.settings import settings

logger = logging.getLogger(__name__)

class MinioClient:
    """
    MinIO (S3兼容) 存储客户端封装。
    用于上传/下载原始素材、成品视频、中间资产，并生成预签名访问 URL。
    """
    def __init__(self):
        self.endpoint = settings.MINIO_ENDPOINT
        self.access_key = settings.MINIO_ACCESS_KEY
        self.secret_key = settings.MINIO_SECRET_KEY
        self.secure = settings.MINIO_SECURE
        
        # 使用 boto3 创建 S3 兼容客户端
        protocol = "https" if self.secure else "http"
        self.s3_client = boto3.client(
            's3',
            endpoint_url=f"{protocol}://{self.endpoint}",
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            config=Config(signature_version='s3v4'),
            region_name='us-east-1' # 对于 MinIO, region 默认即可
        )

    def ensure_bucket_exists(self, bucket_name: str):
        """确保 bucket 存在"""
        try:
            self.s3_client.head_bucket(Bucket=bucket_name)
        except Exception as e:
            logger.info(f"Bucket {bucket_name} does not exist, creating it.")
            self.s3_client.create_bucket(Bucket=bucket_name)

    def upload_file(self, bucket_name: str, object_name: str, file_path: str):
        """上传本地文件到 MinIO"""
        self.ensure_bucket_exists(bucket_name)
        try:
            self.s3_client.upload_file(file_path, bucket_name, object_name)
            logger.info(f"Successfully uploaded {file_path} to {bucket_name}/{object_name}")
            return f"s3://{bucket_name}/{object_name}"
        except Exception as e:
            logger.error(f"Failed to upload {file_path} to MinIO: {e}")
            raise

    def download_file(self, bucket_name: str, object_name: str, dest_path: str):
        """从 MinIO 下载文件到本地"""
        try:
            self.s3_client.download_file(bucket_name, object_name, dest_path)
            logger.info(f"Successfully downloaded {bucket_name}/{object_name} to {dest_path}")
            return dest_path
        except Exception as e:
            logger.error(f"Failed to download {object_name} from MinIO: {e}")
            raise

    def get_presigned_url(self, bucket_name: str, object_name: str, expiration: int = 3600):
        """生成带有效期的预签名 URL，供前端或外部服务直接访问"""
        try:
            response = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket_name, 'Key': object_name},
                ExpiresIn=expiration
            )
            return response
        except Exception as e:
            logger.error(f"Failed to generate presigned URL for {bucket_name}/{object_name}: {e}")
            raise

minio_client = MinioClient()
