export const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";
let accessToken: string | null = null;
export function setToken(token: string | null){
 accessToken=token;
 if(typeof window!="undefined") window.dispatchEvent(new CustomEvent("pathforge:auth-change",{detail:Boolean(token)}));
}
export type Envelope<T>={success:true;data:T};
export async function request<T>(path:string, options:RequestInit={}) : Promise<T>{
 const headers=new Headers(options.headers); headers.set("Content-Type","application/json"); if(accessToken) headers.set("Authorization",`Bearer ${accessToken}`);
 let response=await fetch(`${API}${path}`,{...options,headers,credentials:"include"});
 if(response.status===401 && path!=="/auth/refresh" && typeof window!=="undefined") { const refreshed=await fetch(`${API}/auth/refresh`,{method:"POST",credentials:"include"}); if(refreshed.ok){const body=await refreshed.json();setToken(body.data.access_token);headers.set("Authorization",`Bearer ${body.data.access_token}`);response=await fetch(`${API}${path}`,{...options,headers,credentials:"include"});} }
 if(response.status===204) return undefined as T; const body=await response.json(); if(!response.ok||!body.success) throw new Error(body.error?.message??"Request failed"); return body.data as T;
}
export function post<T>(path:string,data?:unknown){return request<T>(path,{method:"POST",body:data?JSON.stringify(data):undefined})}
export function patch<T>(path:string,data:unknown){return request<T>(path,{method:"PATCH",body:JSON.stringify(data)})}
export function put<T>(path:string,data:unknown){return request<T>(path,{method:"PUT",body:JSON.stringify(data)})}

