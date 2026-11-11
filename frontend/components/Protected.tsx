"use client";
import {useEffect,useState} from "react"; import {useRouter} from "next/navigation"; import {request} from "@/lib/api";
export default function Protected({children}:{children:React.ReactNode}){const [ready,setReady]=useState(false);const router=useRouter();useEffect(()=>{request("/auth/me").then(()=>setReady(true)).catch(()=>router.replace("/login"))},[router]);return ready?<>{children}</>:<div className="container" style={{paddingTop:50}}><div className="skeleton"/></div>}
