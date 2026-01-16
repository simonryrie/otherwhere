"""
Upload destinations data to Firebase Firestore.
Supports both update and overwrite modes.
"""

import json
import logging
import argparse
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, firestore

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def initialize_firebase(credentials_path: str):
    """Initialize Firebase Admin SDK"""
    try:
        cred = credentials.Certificate(credentials_path)
        firebase_admin.initialize_app(cred)
        logger.info("✓ Firebase initialized successfully")
        return firestore.client()
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {e}")
        raise


def load_destinations(file_path: str) -> list:
    """Load destinations from JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        destinations = json.load(f)
    logger.info(f"✓ Loaded {len(destinations)} destinations from {file_path}")
    return destinations


def delete_collection(db, collection_name: str, batch_size: int = 100):
    """Delete all documents in a collection"""
    logger.info(f"Deleting existing collection '{collection_name}'...")

    collection_ref = db.collection(collection_name)
    deleted = 0

    while True:
        docs = collection_ref.limit(batch_size).stream()
        docs_list = list(docs)

        if not docs_list:
            break

        batch = db.batch()
        for doc in docs_list:
            batch.delete(doc.reference)
            deleted += 1

        batch.commit()
        logger.info(f"  Deleted {deleted} documents...")

    logger.info(f"✓ Deleted {deleted} total documents from '{collection_name}'")


def upload_destinations(db, destinations: list, collection_name: str, mode: str = 'overwrite'):
    """
    Upload destinations to Firestore.

    Args:
        db: Firestore client
        destinations: List of destination dictionaries
        collection_name: Name of the Firestore collection
        mode: 'overwrite' (delete + upload) or 'update' (upsert only)
    """

    if mode == 'overwrite':
        delete_collection(db, collection_name)

    logger.info(f"Uploading {len(destinations)} destinations to '{collection_name}'...")

    collection_ref = db.collection(collection_name)
    uploaded = 0
    batch = db.batch()
    batch_size = 500  # Firestore batch limit

    for i, dest in enumerate(destinations):
        # Use destination ID as document ID
        doc_id = dest['id']
        doc_ref = collection_ref.document(doc_id)

        batch.set(doc_ref, dest)
        uploaded += 1

        # Commit batch every 500 documents
        if (i + 1) % batch_size == 0:
            batch.commit()
            logger.info(f"  Uploaded {uploaded}/{len(destinations)} destinations...")
            batch = db.batch()

    # Commit any remaining documents
    if uploaded % batch_size != 0:
        batch.commit()

    logger.info(f"✓ Successfully uploaded {uploaded} destinations to Firestore")


def main():
    parser = argparse.ArgumentParser(description='Upload destinations to Firestore')
    parser.add_argument(
        '--credentials',
        type=str,
        default='firebase-credentials.json',
        help='Path to Firebase service account credentials JSON file'
    )
    parser.add_argument(
        '--data',
        type=str,
        default='data/destinations.json',
        help='Path to destinations JSON file'
    )
    parser.add_argument(
        '--collection',
        type=str,
        default='destinations',
        help='Firestore collection name'
    )
    parser.add_argument(
        '--mode',
        type=str,
        choices=['overwrite', 'update'],
        default='overwrite',
        help='Upload mode: overwrite (delete all + upload) or update (upsert only)'
    )

    args = parser.parse_args()

    # Validate files exist
    if not Path(args.credentials).exists():
        logger.error(f"Credentials file not found: {args.credentials}")
        logger.error("Please download your Firebase service account key and save it as 'firebase-credentials.json'")
        logger.error("Instructions: https://firebase.google.com/docs/admin/setup#python")
        return

    if not Path(args.data).exists():
        logger.error(f"Data file not found: {args.data}")
        return

    logger.info("=" * 60)
    logger.info("FIRESTORE UPLOAD")
    logger.info("=" * 60)
    logger.info(f"Mode: {args.mode}")
    logger.info(f"Collection: {args.collection}")
    logger.info(f"Data file: {args.data}")
    logger.info("=" * 60)

    # Initialize Firebase
    db = initialize_firebase(args.credentials)

    # Load destinations
    destinations = load_destinations(args.data)

    # Upload to Firestore
    upload_destinations(db, destinations, args.collection, mode=args.mode)

    logger.info("=" * 60)
    logger.info("UPLOAD COMPLETE!")
    logger.info("=" * 60)
    logger.info(f"Collection: {args.collection}")
    logger.info(f"Documents: {len(destinations)}")
    logger.info(f"Mode: {args.mode}")


if __name__ == '__main__':
    main()
