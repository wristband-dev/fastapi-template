import { SidebarItem, SsoOptions } from '@/types/sideBarTypes'

/**
 * ============================================
 * SIDEBAR CONFIGURATION
 * ============================================
 * 
 * This file contains all customizable settings for the sidebar.
 * Modify these constants to adjust the appearance and behavior.
 * 
 * Key sections:
 * - APP SETTINGS: Basic app info
 * - LAYOUT DIMENSIONS: Sizes and spacing
 * - VISUAL STYLES: Colors and animations
 * - Z-INDEX LAYERS: Stacking order
 * - NAVIGATION ITEMS: Menu structure
 */

// ============================================
// APP SETTINGS
// ============================================
export const APP_NAME = 'FastAPI Accelerator'

// ============================================
// LAYOUT DIMENSIONS
// ============================================
export const SIDEBAR_WIDTH_OPEN = 256      // Width when sidebar is expanded (desktop)
export const SIDEBAR_WIDTH_CLOSED = 64     // Width when sidebar is collapsed (desktop)
export const TOGGLE_BUTTON_SIZE = 40       // Size of the toggle button
export const MOBILE_TOPBAR_HEIGHT = 56     // Height of mobile top bar (h-14 = 56px)

// ============================================
// VISUAL STYLES
// ============================================
export const HOVER_BG = 'hover:bg-white/10'         // Background on hover
export const DIVIDER_COLOR = 'border-white/10'     // Color of divider lines
export const TRANSITION_DURATION = 300              // Animation duration in milliseconds

// ============================================
// Z-INDEX LAYERS (higher = on top)
// ============================================
export const Z_INDEX = {
  sidebar: 40,          // Main sidebar
  overlay: 30,          // Mobile menu overlay
  logo: 50,            // Logo and toggle button (above sidebar)
}

// ============================================
// NAVIGATION ITEMS
// ============================================
// Main navigation items shown at the top of sidebar
export const sidebarItems: SidebarItem[] = [
  {
    name: 'Home',
    path: '/home',
    icon: 'home',
    showSelected: false    // Don't highlight this item when selected (DEFAULT)
  },
  {
    name: 'Secrets',
    path: '/secrets',
    icon: 'key',
    isAdmin: true
  }
]

// Settings items shown at the bottom of sidebar (above profile)
export const settingsItems: SidebarItem[] = [
  {
    name: 'Billing',
    path: '/billing',
    icon: 'credit-card',
    isAdmin: true
  },
  {
    name: 'Users',
    path: '/users',
    icon: 'users'
  },
  {
    name: 'Admin',
    path: '/admin',
    icon: 'lock',
    isAdmin: true
  }
]

// Profile item shown at the very bottom of sidebar
export const getProfileItem = (givenName: string): SidebarItem => {
  return {
    name: givenName,
    path: '/profile',
    icon: 'user'
  }
}

// ============================================
// SSO OPTIONS for Admin section
// ============================================
export const ssoOptions: SsoOptions = {
  googleSSOIDP: true,
  oktaSSOIDP: true
}