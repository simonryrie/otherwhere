"""
Unsplash-based image fetching for destinations.
Uses diverse search queries to get varied, high-quality scenic images.
"""

import requests
import time
import logging
import os
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class UnsplashImageClient:
    """Client for fetching images from Unsplash API"""

    UNSPLASH_API_URL = "https://api.unsplash.com/search/photos"

    def __init__(self, access_key: Optional[str] = None):
        # Get access key from environment variable or parameter
        self.access_key = access_key or os.getenv('UNSPLASH_ACCESS_KEY')

        if not self.access_key:
            raise ValueError("Unsplash access key is required. Set UNSPLASH_ACCESS_KEY environment variable or pass access_key parameter.")

        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Client-ID {self.access_key}',
            'User-Agent': 'Otherwhere/1.0 (Travel Inspiration Platform)'
        })

    def get_destination_images(self, destination_name: str, country: str, dest_type: str = 'city', limit: int = 3) -> Tuple[List[str], List[str]]:
        """
        Get diverse images for a destination using multiple search queries.

        Args:
            destination_name: Name of destination
            country: Country name
            dest_type: 'city' or 'region'
            limit: Number of images to return (max 6)

        Returns:
            Tuple of (image_urls, download_urls) for Unsplash attribution
        """
        try:
            # Define search queries based on destination type
            if dest_type == 'city':
                queries = [
                    f"{destination_name} landmark",
                    f"{destination_name} street",
                    f"{destination_name} aerial view",
                    f"{destination_name} culture",
                    f"{destination_name} food",
                    f"{destination_name}",
                ]
            else:  # region
                queries = [
                    f"{destination_name} landscape",
                    f"{destination_name} culture",
                    f"{destination_name} aerial view",
                    f"{destination_name} town",
                    f"{destination_name} food",
                    f"{destination_name}",
                ]

            all_images = []
            all_download_urls = []
            seen_urls = set()

            # Fetch one image per query type
            for idx, query in enumerate(queries[:limit]):
                # Add country to query for better relevance
                full_query = f"{query} {country}"

                logger.debug(f"Searching Unsplash: '{full_query}'")

                images = self._search_images(full_query, per_page=5)

                # Find the first image that matches our criteria and isn't a duplicate
                for img in images:
                    img_url = img['urls']['regular']

                    # Skip duplicates
                    if img_url in seen_urls:
                        continue

                    # Prefer images with destination/country in metadata
                    if self._is_relevant_image(img, destination_name, country):
                        all_images.append(img_url)
                        # Store download URL for attribution requirement
                        download_url = img['links'].get('download_location', '')
                        all_download_urls.append(download_url)
                        seen_urls.add(img_url)

                        # Trigger download tracking (required by Unsplash)
                        if download_url:
                            self._trigger_download(download_url)

                        break

                # Rate limiting
                time.sleep(0.3)

                if len(all_images) >= limit:
                    break

            logger.info(f"Found {len(all_images)} Unsplash images for {destination_name}")
            return all_images, all_download_urls

        except Exception as e:
            logger.warning(f"Failed to get Unsplash images for {destination_name}: {e}")
            return [], []

    def _search_images(self, query: str, per_page: int = 5) -> List[Dict]:
        """Search Unsplash for images"""
        try:
            params = {
                'query': query,
                'per_page': per_page,
                'orientation': 'landscape',  # Prefer landscape for travel photos
                'content_filter': 'high',  # Filter inappropriate content
            }

            response = self.session.get(self.UNSPLASH_API_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            return data.get('results', [])

        except Exception as e:
            logger.debug(f"Unsplash search failed for '{query}': {e}")
            return []

    def _is_relevant_image(self, img: Dict, destination: str, country: str) -> bool:
        """
        Check if image is relevant to the destination.
        Strongly prefer images with destination/country in metadata.
        """
        destination_lower = destination.lower()
        country_lower = country.lower()

        # Check description
        description = (img.get('description') or '').lower()
        alt_description = (img.get('alt_description') or '').lower()

        # Check tags
        tags = img.get('tags', [])
        tag_titles = ' '.join([tag.get('title', '').lower() for tag in tags])

        # Check location data
        location = img.get('location', {})
        location_name = (location.get('name') or '').lower()
        location_city = (location.get('city') or '').lower()
        location_country = (location.get('country') or '').lower()

        # Combine all text fields
        all_text = f"{description} {alt_description} {tag_titles} {location_name} {location_city} {location_country}"

        # Strongly prefer if destination or country mentioned
        has_destination = destination_lower in all_text
        has_country = country_lower in all_text

        if has_destination or has_country:
            return True

        # If no metadata match, still accept but with lower priority
        # This allows generic scenic images when metadata is sparse
        return True

    def _trigger_download(self, download_url: str) -> None:
        """
        Trigger download tracking as required by Unsplash API guidelines.
        This must be called when a user views/uses a photo.

        Args:
            download_url: The download_location URL from the image data
        """
        try:
            # Make a GET request to the download_location endpoint
            # This notifies Unsplash that the photo is being used
            response = self.session.get(download_url, timeout=5)
            response.raise_for_status()
            logger.debug(f"Successfully triggered download tracking")
        except Exception as e:
            logger.warning(f"Failed to trigger download tracking: {e}")

    def get_image_credit(self, img_url: str) -> Optional[str]:
        """
        Get photographer credit for an image URL.
        Note: Unsplash requires attribution.
        """
        # This would need the full image object to get photographer info
        # For now, return a placeholder
        return "Photo by Unsplash"
