# 📊 Survey AI - Full Stack Data Explorer

A modern, professional full-stack application for exploring and analyzing survey datasets dynamically with beautiful visualizations and an intuitive user interface.

## 🎯 Features

- **Dynamic Dataset Explorer**: Browse and explore multiple datasets without hardcoded queries
- **Advanced Filtering**: Real-time filtering with support for text, numeric ranges, and dates
- **Data Visualization**: Interactive charts with Bar, Line, Pie, and multi-series visualizations
- **Responsive Design**: Works seamlessly on desktop and tablet devices
- **Modern UI/UX**: Professional styling with Tailwind CSS and shadcn/ui components
- **Secure Backend**: Parameterized SQL queries to prevent injection attacks
- **Authentication**: JWT-based authentication with persistent sessions

## 🏗️ Architecture

### Frontend
- **Framework**: React 18.2.0 with Vite build tool
- **Styling**: Tailwind CSS 3.3.0
- **Components**: shadcn/ui + lucide-react icons
- **Visualization**: recharts for interactive charts
- **HTTP Client**: Axios
- **Routing**: React Router v6

### Backend
- **Framework**: FastAPI 0.115.6
- **Database**: PostgreSQL 15.14
- **ORM**: SQLAlchemy with connection pooling
- **Security**: Parameterized queries, input validation

## 📁 Project Structure

```
survey-ai-app/
├── backend/
│   ├── main.py           # FastAPI application with all endpoints
│   ├── requirements.txt   # Python dependencies
│   └── .env             # Environment variables (create from .env.example)
│
├── frontend/
│   ├── src/
│   │   ├── main.jsx              # React entry point
│   │   ├── App.jsx               # Main app component with routing
│   │   ├── index.css             # Tailwind directives + custom styles
│   │   ├── pages/
│   │   │   ├── Login.jsx         # Authentication page
│   │   │   ├── Dashboard.jsx     # Main dashboard overview
│   │   │   ├── SurveyAI.jsx      # Data explorer page
│   │   │   └── Settings.jsx      # User settings
│   │   └── components/
│   │       ├── Navbar.jsx        # Top navigation bar
│   │       ├── Sidebar.jsx       # Left navigation
│   │       ├── DatasetSelector.jsx   # Dataset dropdown
│   │       ├── ColumnSelector.jsx    # Column selection
│   │       ├── FiltersPanel.jsx      # Dynamic filters
│   │       ├── DataTable.jsx         # Data display table
│   │       └── ChartView.jsx         # Data visualizations
│   ├── index.html        # HTML entry point
│   ├── vite.config.js    # Vite configuration
│   ├── tailwind.config.js # Tailwind configuration
│   ├── postcss.config.js  # PostCSS configuration
│   └── package.json      # Node dependencies
```

## 🚀 Getting Started

### Prerequisites
- Node.js 16+ and npm or yarn
- Python 3.10+
- PostgreSQL 12+

### Backend Setup

1. **Navigate to backend directory**
```bash
cd survey-ai-app/backend
```

2. **Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Create environment file**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

5. **Run the backend**
```bash
python main.py
```
The backend runs on `http://localhost:8001`

### Frontend Setup

1. **Navigate to frontend directory**
```bash
cd survey-ai-app/frontend
```

2. **Install dependencies**
```bash
npm install  # or yarn install
```

3. **Run development server**
```bash
npm run dev  # or yarn dev
```
The frontend runs on `http://localhost:5173`

4. **Access the application**
Open your browser and visit `http://localhost:5173`

## 📱 Usage

### Login
- Use the demo credentials or click "Try Demo" for quick access
- Demo account email: `demo@survey-ai.com`

### Dashboard
- View overview statistics of available datasets
- Navigate between different sections with the sidebar

### Survey AI (Data Explorer)
1. **Select Dataset**: Choose a dataset from the dropdown
2. **Choose Columns**: Select which columns to display
3. **Apply Filters**: Use dynamic filters based on column types
4. **View Data**: Browse results in the interactive table
5. **Explore Charts**: View automatic visualizations

## 🔌 API Endpoints

### Public Endpoints
- `GET /health` - Health check
- `GET /datasets` - List all available datasets
- `GET /columns/{table}` - Get columns for a dataset
- `POST /data` - Fetch filtered data
- `GET /statistics/{table}` - Get aggregate statistics

### Request/Response Examples

**Fetch Data**
```bash
curl -X POST http://localhost:8001/data \
  -H "Content-Type: application/json" \
  -d '{
    "table": "your_table",
    "columns": ["col1", "col2"],
    "filters": {"col1": "value"},
    "limit": 10,
    "offset": 0
  }'
```

## 🛡️ Security Features

- ✅ Parameterized SQL queries prevent SQL injection
- ✅ Input validation on table and column names
- ✅ CORS configured for local development
- ✅ JWT-based authentication
- ✅ Secure password handling

## 🎨 UI/UX Design

- **Color Scheme**: Blue-Purple gradient (modern SaaS style)
- **Typography**: Inter font family for clarity
- **Spacing**: Consistent 8px grid system
- **Shadows**: Subtle elevation effects
- **Transitions**: Smooth animations for interactions
- **Accessibility**: ARIA labels and keyboard navigation

## 📊 Component Details

### DatasetSelector
- Searchable dropdown
- Icon indicators
- Count of available datasets

### ColumnSelector
- Grid of selectable columns
- Show column data types
- Display selection count

### FiltersPanel
- Type-aware filter inputs
- Numeric range filters for numbers
- Text search for strings
- Date pickers for dates
- Active filter badges

### DataTable
- Sortable columns
- Global search functionality
- Pagination controls
- Sticky header
- Responsive scrolling
- Row highlighting on hover

### ChartView
- Bar charts for distribution
- Line charts for trends
- Pie charts for categories
- Multi-series comparisons
- Recharts integration

## ⚙️ Configuration

### Environment Variables (.env)
```
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=survey_db
```

### Tailwind Customization
Edit `tailwind.config.js` to customize:
- Colors (gradient-start, gradient-end)
- Typography (fonts)
- Spacing (scale)
- Shadows (effects)

## 🐛 Troubleshooting

### Backend Connection Issues
- Verify PostgreSQL is running
- Check database credentials in `.env`
- Ensure port 8001 is available

### Frontend Won't Load
- Clear browser cache
- Delete node_modules and reinstall: `npm install`
- Restart development server

### Charts Not Showing
- Verify data includes numeric columns
- Check filter results aren't empty
- Inspect browser console for errors

## 📚 Technologies Used

### Frontend
- React 18.2.0
- Vite 5.0+
- Tailwind CSS 3.3.0
- Recharts 2.10+
- Lucide React (icons)
- Axios (HTTP)
- React Router v6

### Backend
- FastAPI 0.115.6
- PostgreSQL 15.14
- SQLAlchemy 2.0+
- Pydantic
- psycopg2-binary

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🎓 Learning Resources

- [React Documentation](https://react.dev)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Tailwind CSS](https://tailwindcss.com)
- [PostgreSQL Documentation](https://www.postgresql.org/docs)

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review API documentation
3. Inspect browser/server console logs
4. Create an issue with details

---

**Built with ❤️ for modern data exploration**
