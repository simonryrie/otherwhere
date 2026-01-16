/**
 * UnsplashImage component with proper attribution
 * Displays an image with photographer credit and Unsplash link as required by Unsplash API guidelines
 */

import React from 'react';

interface UnsplashImageProps {
  /** Image URL from Unsplash */
  imageUrl: string;
  /** Photographer's full name */
  photographerName: string;
  /** Photographer's Unsplash profile URL */
  photographerUrl: string;
  /** Alt text for the image */
  alt: string;
  /** Optional: Download location URL for tracking (triggers download on click) */
  downloadLocation?: string;
}

export const UnsplashImage: React.FC<UnsplashImageProps> = ({
  imageUrl,
  photographerName,
  photographerUrl,
  alt,
  downloadLocation,
}) => {
  const handleImageLoad = () => {
    // Trigger download tracking when image is displayed
    // This is required by Unsplash API guidelines
    if (downloadLocation) {
      fetch(downloadLocation).catch((err) =>
        console.error('Failed to trigger Unsplash download tracking:', err)
      );
    }
  };

  return (
    <div style={{ position: 'relative', display: 'inline-block', maxWidth: '100%' }}>
      {/* Image */}
      <img
        src={imageUrl}
        alt={alt}
        onLoad={handleImageLoad}
        style={{
          width: '100%',
          height: 'auto',
          display: 'block',
          borderRadius: '8px',
        }}
      />

      {/* Attribution overlay */}
      <div
        style={{
          position: 'absolute',
          bottom: '8px',
          left: '8px',
          right: '8px',
          backgroundColor: 'rgba(0, 0, 0, 0.6)',
          color: 'white',
          padding: '6px 10px',
          borderRadius: '4px',
          fontSize: '12px',
          backdropFilter: 'blur(4px)',
        }}
      >
        Photo by{' '}
        <a
          href={`${photographerUrl}?utm_source=otherwhere&utm_medium=referral`}
          target="_blank"
          rel="noopener noreferrer"
          style={{
            color: 'white',
            textDecoration: 'underline',
            fontWeight: 500,
          }}
        >
          {photographerName}
        </a>{' '}
        on{' '}
        <a
          href="https://unsplash.com?utm_source=otherwhere&utm_medium=referral"
          target="_blank"
          rel="noopener noreferrer"
          style={{
            color: 'white',
            textDecoration: 'underline',
            fontWeight: 500,
          }}
        >
          Unsplash
        </a>
      </div>
    </div>
  );
};
