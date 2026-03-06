/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    API_BASE_URL: process.env.API_BASE_URL || 'http://localhost:8000',
    WS_BASE_URL: process.env.WS_BASE_URL || 'ws://localhost:8000'
  }
}

module.exports = nextConfig
