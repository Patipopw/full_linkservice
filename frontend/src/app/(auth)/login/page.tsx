'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Cookies from 'js-cookie';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const router = useRouter();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const res = await fetch('http://localhost:8000/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData.toString(),
    });

    if (res.ok) {
      const data = await res.json();
      Cookies.set('access_token', data.access_token, { expires: 1 });
      Cookies.set("user_full_name", data.user.full_name);
      Cookies.set("user_id", String(data.user.id));
      Cookies.set("user_email", data.user.email);

      router.push('/dashboard');
    } else {
      alert("Login Failed");
    }
  };

  return (
    <div className="flex h-screen items-center justify-center bg-slate-50">
      <Card className="w-87.5">
        <CardHeader><CardTitle className="text-center text-black">Login</CardTitle></CardHeader>
        <CardContent>
          <form onSubmit={handleLogin} className="space-y-4 text-black">
            <Input type="email" placeholder="Email" onChange={(e) => setEmail(e.target.value)} required />
            <Input type="password" placeholder="Password" onChange={(e) => setPassword(e.target.value)} required />
            <Button type="submit" className="w-full">Sign In</Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}