import { useEffect } from 'react';

export default function AdBanner({ slot, format = 'auto', responsive = true, style = {} }) {
  useEffect(() => {
    try {
      // Push ad to AdSense
      if (window.adsbygoogle && process.env.NODE_ENV === 'production') {
        (window.adsbygoogle = window.adsbygoogle || []).push({});
      }
    } catch (err) {
      console.error('AdSense error:', err);
    }
  }, []);

  // Don't show ads in development
  if (process.env.NODE_ENV !== 'production') {
    return (
      <div style={{
        background: 'rgba(255,255,255,0.05)',
        border: '1px dashed rgba(255,255,255,0.2)',
        borderRadius: '8px',
        padding: '20px',
        textAlign: 'center',
        color: 'rgba(255,255,255,0.4)',
        fontSize: '12px',
        ...style
      }}>
        Ad Space (Shows in production)
      </div>
    );
  }

  return (
    <div style={{ margin: '20px 0', textAlign: 'center', ...style }}>
      <ins
        className="adsbygoogle"
        style={{ display: 'block', ...style }}
        data-ad-client="ca-pub-XXXXXXXXXXXXXXXX"
        data-ad-slot={slot}
        data-ad-format={format}
        data-full-width-responsive={responsive.toString()}
      />
    </div>
  );
}

// Predefined ad components for easy use
export function TopBannerAd() {
  return (
    <AdBanner
      slot="1234567890"
      format="horizontal"
      style={{ minHeight: '90px' }}
    />
  );
}

export function SidebarAd() {
  return (
    <AdBanner
      slot="0987654321"
      format="vertical"
      style={{ minWidth: '160px', minHeight: '600px' }}
    />
  );
}

export function InFeedAd() {
  return (
    <AdBanner
      slot="1122334455"
      format="fluid"
      style={{ minHeight: '250px' }}
    />
  );
}
