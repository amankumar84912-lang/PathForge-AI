import "./globals.css";
import Link from "next/link";
import TopNav from "@/components/TopNav";
export const metadata = { title: "PathForge AI", description: "Personalized, prerequisite-aware career roadmaps" };
export default function RootLayout({children}:{children:React.ReactNode}) { return <html lang="en"><body><header className="topbar"><div className="container" style={{display:"flex",justifyContent:"space-between",alignItems:"center",width:"100%"}}><Link className="brand" href="/"><span className="brand-mark">↗</span>PathForge AI</Link><TopNav /></div></header>{children}</body></html> }

