import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  // 1. ดึง Token จาก Cookie
  const token = request.cookies.get('access_token')?.value
  const { pathname } = request.nextUrl

  // 2. ถ้าไม่มี Token และพยายามเข้าหน้าในกลุ่ม Dashboard
  // (แก้เงื่อนไขให้ตรงกับ URL จริงของคุณ เช่น /dashboard หรือ /sale)
  const isDashboardPage = pathname.startsWith('/dashboard') || 
                          pathname.startsWith('/sale') || 
                          pathname.startsWith('/profile');

  if (isDashboardPage && !token) {
    // ส่งกลับไปหน้า Login ทันที
    return NextResponse.redirect(new URL('/login', request.url))
  }

  // 3. ถ้ามี Token แล้วแต่พยายามจะไปหน้า Login อีก
  if (token && pathname === '/login') {
    // ส่งไปหน้า Dashboard แทน
    return NextResponse.redirect(new URL('/dashboard', request.url))
  }

  return NextResponse.next()
}

// 4. กำหนด Path ที่ต้องการให้ Middleware นี้ทำงาน
export const config = {
  matcher: [
    '/dashboard/:path*', 
    '/sale/:path*', 
    '/profile/:path*', 
    '/login'
  ],
}