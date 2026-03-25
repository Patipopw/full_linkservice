"use client"

import * as React from "react"
import Cookies from "js-cookie"
import {
  LayoutDashboardIcon,
  FileTextIcon,
  TerminalIcon,
} from "lucide-react"

import { NavMain } from "@/components/nav-main"
import { NavSecondary } from "@/components/nav-secondary"
import { NavUser } from "@/components/nav-user"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar"
import { toast } from "sonner"

// 1. ปรับข้อมูล Menu ให้ตรงกับ Sale, Profile, Dashboard
const data = {
  navMain: [
    {
      title: "Dashboard",
      url: "/dashboard",
      icon: <LayoutDashboardIcon />,
      isActive: true,
    },
    {
      title: "Sale System",
      url: "#", 
      icon: <FileTextIcon />,
      items: [
        {
          title: "Quotation",
          url: "/sale/quotation",
        },
        {
          title: "Sale Order",
          url: "/sale/sale-order",
        },
        {
          title: "Invoice",
          url: "/sale/invoice",
        },
      ],
    },
  ],
  navSecondary: [
    // {
    //   title: "Support",
    //   url: "#",
    //   icon: <LifeBuoyIcon />,
    // },
    // {
    //   title: "Feedback",
    //   url: "#",
    //   icon: <SendIcon />,
    // },
  ],
}

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  const [userData, setUserData] = React.useState({
    full_name: "Loading...",
    email: "fetching data...",
    avatar: ""
  })

  React.useEffect(() => {
    const fetchUser = async () => {
      const token = Cookies.get("access_token")
      if (!token) {
        window.location.href = "/login"
        return
      }

      try {
        const res = await fetch("http://localhost:8000/me", {
          headers: { "Authorization": `Bearer ${token}` }
        })

        if (res.status === 401) {
          toast.error("เซสชั่นหมดอายุ", {
            description: "กรุณาเข้าสู่ระบบใหม่อีกครั้ง",
          })
          Cookies.remove("access_token") // ล้าง Token ที่หมดอายุ
          window.location.href = "/login" // ดีดกลับไปหน้า Login
          return
        }
        
        if (res.ok) {
          const resData = await res.json()
          setUserData({
            full_name: resData.full_name || resData.nickname || resData.email,
            email: resData.email,
            avatar: `https://api.dicebear.com{resData.email}`
          })
        }
      } catch (err) {
        console.error("Fetch user error:", err)
      }
    }
    fetchUser()
  }, [])

  return (
    <Sidebar variant="inset" {...props}>
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton size="lg" asChild>
              <a href="/dashboard">
                <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground">
                  <TerminalIcon className="size-4" />
                </div>
                <div className="grid flex-1 text-left text-sm leading-tight text-black">
                  <span className="truncate font-medium">Sale System</span>
                  <span className="truncate text-xs">Management</span>
                </div>
              </a>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>
      <SidebarContent>
        {/* ส่งข้อมูล navMain ที่แก้ไขใหม่ไปแสดงผล */}
        <NavMain items={data.navMain} />
        <NavSecondary items={data.navSecondary} className="mt-auto" />
      </SidebarContent>
      <SidebarFooter>
        <NavUser user={userData} />
      </SidebarFooter>
    </Sidebar>
  )
}