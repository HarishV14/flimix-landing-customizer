# Flimix Page Builder

A visual drag-and-drop page builder for creating landing pages with movie and series content.

## 🚀 Features

### **Visual Page Builder**
- **Drag & Drop Sections**: Add different section types to your landing page
- **Live Preview**: See changes in real-time with responsive viewport simulation
- **Content Management**: Add movies and series to sections with drag & drop
- **Properties Panel**: Customize section settings and styling

### **Section Types**
- **Hero Section**: Full-width hero with background image and call-to-action
- **Movie Carousel**: Horizontal scrolling carousel of movies/series
- **Content Grid**: Responsive grid layout for content
- **Featured Content**: Highlighted section for featured items
- **Text Section**: Rich text content with formatting
- **Promotional Banner**: Promotional banner with image overlay

### **Content Management**
- **Drag & Drop**: Drag movies/series from library to sections
- **Search & Filter**: Find content by title, description, or type
- **Visual Feedback**: See what you're dragging with overlay preview
- **Reorder Content**: Move content up/down within sections

## 🛠️ How to Use

### **1. Select a Landing Page**
- Choose an existing landing page from the dropdown
- Or create a new one in the Django admin

### **2. Add Sections**
- Drag section templates from the left sidebar to the canvas
- Each section type has different content capabilities

### **3. Manage Content**
- Click "Manage Content" on any section
- Drag movies/series from the left panel to the right panel
- Or click "Add" button for individual items

### **4. Customize Sections**
- Select a section to open the properties panel
- Edit title, subtitle, colors, and other settings
- For text sections, edit the content directly

### **5. Preview & Save**
- Use viewport controls to see how it looks on different devices
- Toggle preview mode to see the final result
- Click "Save" to persist your changes

## 🎯 Quick Start

1. **Start the Django backend**:
   ```bash
   cd flimix_api
   python manage.py runserver 8002
   ```

2. **Start the React frontend**:
   ```bash
   cd flimix-admin
   npm run dev
   ```

3. **Open the Page Builder**:
   - Navigate to `http://localhost:5173`
   - Select a landing page
   - Start building!

## 📁 Project Structure

```
flimix-admin/
├── src/
│   ├── pages/
│   │   └── PageBuilder.jsx          # Main page builder component
│   ├── components/
│   │   └── ContentManager.jsx       # Content management modal
│   └── lib/
│       └── api.js                   # API endpoints
└── README.md
```

## 🔧 Technical Details

- **Frontend**: React with Vite, Tailwind CSS
- **Backend**: Django with REST API
- **State Management**: React Query for server state
- **Drag & Drop**: HTML5 Drag and Drop API
- **Styling**: Tailwind CSS with responsive design

## 🎨 Customization

### **Adding New Section Types**
1. Add the section template to `sectionTemplates` array
2. Add the rendering logic in `renderSectionPreview`
3. Add properties in `SectionProperties` component

### **Styling**
- All styling is done with Tailwind CSS
- Responsive design with mobile, tablet, and desktop viewports
- Custom colors and themes can be modified in `tailwind.config.js`

## 🐛 Troubleshooting

### **Common Issues**
- **API Errors**: Make sure Django backend is running on port 8002
- **Drag & Drop Not Working**: Check browser console for errors
- **Content Not Loading**: Verify API endpoints in `api.js`

### **Development**
- Check browser console for detailed error messages
- Use React DevTools for component debugging
- Network tab for API request debugging
