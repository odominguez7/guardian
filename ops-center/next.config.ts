import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Hide Next.js dev indicators (the "N" badge and route/issues bubble) so
  // they don't appear in demo-video recording captures.
  devIndicators: false,
};

export default nextConfig;
