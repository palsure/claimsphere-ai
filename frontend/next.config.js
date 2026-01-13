/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  
  // Disable webpack eval in development to avoid CSP issues
  webpack: (config, { dev, isServer }) => {
    if (dev && !isServer) {
      // Use 'cheap-module-source-map' instead of 'eval' for better CSP compatibility
      // This prevents CSP errors while still providing source maps for debugging
      config.devtool = 'cheap-module-source-map';
    }
    return config;
  },
  
  // API calls now use direct URLs with NEXT_PUBLIC_API_URL
  // Rewrites kept as fallback but direct URLs are preferred
  async rewrites() {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    return [
      {
        source: '/api/:path*',
        destination: `${apiUrl}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;

