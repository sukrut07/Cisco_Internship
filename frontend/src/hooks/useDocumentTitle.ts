import { useEffect } from 'react';

const APP_NAME = 'NetSage AI';

/**
 * Sets the document title for a given route.
 * Format: "NetSage AI — {pageTitle}"
 */
export function useDocumentTitle(pageTitle: string) {
  useEffect(() => {
    const previous = document.title;
    document.title = `${APP_NAME} — ${pageTitle}`;
    return () => {
      document.title = previous;
    };
  }, [pageTitle]);
}
