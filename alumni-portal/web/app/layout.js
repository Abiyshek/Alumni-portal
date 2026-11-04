import { Inter, Plus_Jakarta_Sans } from "next/font/google";
import Footer from "@/components/Footer";
import Nav from "@/components/Nav";
import Providers from "@/components/Providers";
import "./globals.css";

const display = Plus_Jakarta_Sans({ subsets: ["latin"], variable: "--font-jakarta", display: "swap" });
const body = Inter({ subsets: ["latin"], variable: "--font-inter", display: "swap" });

export const metadata = {
  title: { default: "Alumni Association · PM SHRI KV No. 2 Pondicherry", template: "%s · KV No. 2 Pondicherry Alumni" },
  description: "The alumni network of PM SHRI Kendriya Vidyalaya No. 2 Pondicherry, Kalapet. Find classmates, join reunions, share opportunities.",
};

export const viewport = { themeColor: "#0d3384" };

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={`${display.variable} ${body.variable}`}>
      <body>
        <Providers>
          <Nav />
          <main className="main wrap">{children}</main>
          <Footer />
        </Providers>
      </body>
    </html>
  );
}
