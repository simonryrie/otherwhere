/**
 * Demo page for Unsplash Attribution
 *
 * NOTE: This is a demo component created for screenshot purposes to show
 * Unsplash API compliance. The actual UI is not yet built - this demonstrates
 * the required attribution format as per Unsplash API guidelines.
 */

import React from "react";
import { UnsplashImage } from "../components/UnsplashImage";

export const AttributionDemo: React.FC = () => {
  return (
    <div
      style={{
        padding: "40px",
        maxWidth: "1200px",
        margin: "0 auto",
        fontFamily:
          '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      }}
    >
      {/* Demo Notice */}
      <div
        style={{
          backgroundColor: "#f0f9ff",
          border: "2px solid #0ea5e9",
          borderRadius: "8px",
          padding: "20px",
          marginBottom: "40px",
        }}
      >
        <h3 style={{ margin: "0 0 10px 0", color: "#0369a1" }}>
          📸 Unsplash Attribution Demo
        </h3>
        <p style={{ margin: 0, color: "#075985", lineHeight: 1.6 }}>
          <strong>Note:</strong> The UI shown below is for demonstration
          purposes only to show Unsplash API compliance. The actual application
          interface is not yet built. This demonstrates the required attribution
          format with photographer credit and Unsplash link as specified in the
          Unsplash API guidelines.
        </p>
      </div>

      {/* Sample Destination Card */}
      <div
        style={{
          backgroundColor: "white",
          borderRadius: "12px",
          overflow: "hidden",
          boxShadow:
            "0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)",
          marginBottom: "40px",
        }}
      >
        <UnsplashImage
          imageUrl="https://images.unsplash.com/photo-1584451655678-61594db5f728?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w4NTUwMzJ8MHwxfHNlYXJjaHwxfHxBbGdhcnZlJTIwUG9ydHVnYWx8ZW58MXwwfHx8MTc2Nzk4NTYwMnww&ixlib=rb-4.1.0&q=80&w=1080"
          photographerName="Annie Spratt"
          photographerUrl="https://unsplash.com/@anniespratt"
          alt="Scenic view of Algarve, Portugal"
          downloadLocation="https://api.unsplash.com/photos/TElzaVit720/download?ixid=M3w4NTUwMzJ8MHwxfHNlYXJjaHwxfHxBbGdhcnZlJTIwUG9ydHVnYWx8ZW58MXwwfHx8MTc2Nzk4NTYwMnww"
        />

        <div style={{ padding: "20px" }}>
          <h2 style={{ margin: "0 0 10px 0", color: "#1e293b" }}>
            Algarve, Portugal
          </h2>
          <p style={{ margin: 0, color: "#64748b", lineHeight: 1.6 }}>
            Discover the stunning coastal region of southern Portugal with its
            golden beaches, dramatic cliffs, and charming fishing villages.
          </p>
        </div>
      </div>

      {/* Attribution Explanation */}
      <div
        style={{
          backgroundColor: "#f8fafc",
          border: "1px solid #e2e8f0",
          borderRadius: "8px",
          padding: "20px",
        }}
      >
        <h3 style={{ margin: "0 0 15px 0", color: "#475569" }}>
          ✓ Unsplash API Compliance
        </h3>
        <ul
          style={{
            margin: 0,
            paddingLeft: "20px",
            color: "#64748b",
            lineHeight: 1.8,
          }}
        >
          <li>
            Photographer's full name is displayed and linked to their Unsplash
            profile
          </li>
          <li>"Unsplash" is displayed and linked to unsplash.com</li>
          <li>
            Attribution follows the format: "Photo by [Photographer Name] on
            Unsplash"
          </li>
          <li>UTM parameters are included in links for proper tracking</li>
          <li>Download tracking is triggered when images are displayed</li>
        </ul>
      </div>

      {/* URL Display Section */}
      <div
        style={{
          backgroundColor: "#fff",
          border: "2px solid #10b981",
          borderRadius: "8px",
          padding: "20px",
          marginTop: "20px",
        }}
      >
        <h3 style={{ margin: "0 0 15px 0", color: "#059669" }}>
          📋 Actual URLs (for verification)
        </h3>

        <div style={{ marginBottom: "15px" }}>
          <div style={{ fontSize: "13px", fontWeight: "600", color: "#374151", marginBottom: "5px" }}>
            Photographer Link:
          </div>
          <code style={{
            display: "block",
            padding: "10px",
            backgroundColor: "#f3f4f6",
            borderRadius: "4px",
            fontSize: "11px",
            wordBreak: "break-all",
            color: "#1f2937",
            fontFamily: "monospace"
          }}>
            https://unsplash.com/@anniespratt?utm_source=otherwhere&utm_medium=referral
          </code>
        </div>

        <div>
          <div style={{ fontSize: "13px", fontWeight: "600", color: "#374151", marginBottom: "5px" }}>
            Unsplash Link:
          </div>
          <code style={{
            display: "block",
            padding: "10px",
            backgroundColor: "#f3f4f6",
            borderRadius: "4px",
            fontSize: "11px",
            wordBreak: "break-all",
            color: "#1f2937",
            fontFamily: "monospace"
          }}>
            https://unsplash.com?utm_source=otherwhere&utm_medium=referral
          </code>
        </div>

        <p style={{
          marginTop: "15px",
          marginBottom: 0,
          fontSize: "13px",
          color: "#6b7280",
          fontStyle: "italic"
        }}>
          💡 Hover over the attribution links on the image above to see these URLs in your browser's bottom-left corner
        </p>
      </div>
    </div>
  );
};
