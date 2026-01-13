import { Html, Head, Main, NextScript } from 'next/document';

export default function Document() {
  return (
    <Html>
      <Head>
        {/* Meta tag to allow unsafe-eval in development (Next.js requirement) */}
        {process.env.NODE_ENV === 'development' && (
          <meta
            httpEquiv="Content-Security-Policy"
            content="script-src 'self' 'unsafe-inline' 'unsafe-eval'; object-src 'none';"
          />
        )}
        {/* Prevent flash of wrong theme */}
        <script
          dangerouslySetInnerHTML={{
            __html: `
              (function() {
                try {
                  var theme = localStorage.getItem('theme');
                  var prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
                  var initialTheme = theme || (prefersDark ? 'dark' : 'light');
                  document.documentElement.setAttribute('data-theme', initialTheme);
                } catch (e) {}
              })();
            `,
          }}
        />
      </Head>
      <body>
        <Main />
        <NextScript />
      </body>
    </Html>
  );
}
