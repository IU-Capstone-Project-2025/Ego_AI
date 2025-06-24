import React, { useState, useEffect, useCallback } from 'react';
import { format, startOfWeek, addDays, addWeeks, subWeeks, isToday } from 'date-fns';
import './Calendar.css';

// Types for our calendar events
interface CalendarEvent {
  id: string;
  title: string;
  start: Date;
  end: Date;
  type: 'focus' | 'tasks' | 'target' | 'other';
  description?: string;
}

interface TaskForm {
  title: string;
  duration: number;
  type: 'focus' | 'tasks' | 'target' | 'other';
  description: string;
  dueDate: string;
  dueTime: string;
}

// Google Calendar API configuration
const GOOGLE_API_KEY = import.meta.env.VITE_GOOGLE_API_KEY;
const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID;
const DISCOVERY_DOC = 'https://www.googleapis.com/discovery/v1/apis/calendar/v3/rest';
const SCOPES = 'https://www.googleapis.com/auth/calendar';

// Environment variables are loaded successfully

declare global {
  interface Window {
    gapi: any;
    google: any;
    googleTokenClient: any;
  }
}

export const Calendar: React.FC = () => {
  // State management
  const [currentDate, setCurrentDate] = useState(new Date());
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [weeklyHours, setWeeklyHours] = useState({
    focus: 0,
    tasks: 0,
    target: 0,
    other: 0,
    free: 119
  });
  const [isGoogleApiLoaded, setIsGoogleApiLoaded] = useState(false);
  const [isSignedIn, setIsSignedIn] = useState(false);
  const [gapi, setGapi] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'disconnected' | 'connecting' | 'connected' | 'error'>('disconnected');
  const [accessToken, setAccessToken] = useState<string | null>(null);
  
  // Task form state - use current viewing date instead of today
  const [taskForm, setTaskForm] = useState<TaskForm>({
    title: '',
    duration: 1,
    type: 'tasks',
    description: '',
    dueDate: format(currentDate, 'yyyy-MM-dd'),
    dueTime: '18:00'
  });

  // Update task form date when currentDate changes
  const updateTaskFormDate = () => {
    setTaskForm(prev => ({
      ...prev,
      dueDate: format(currentDate, 'yyyy-MM-dd')
    }));
  };

  // Calculate hours for each task type in the current week
  const calculateWeeklyHours = useCallback(() => {
    const weekStart = startOfWeek(currentDate);
    const weekEnd = addDays(weekStart, 6);
    
    // Filter events for current week
    const weekEvents = events.filter(event => {
      const eventDate = new Date(event.start);
      return eventDate >= weekStart && eventDate <= weekEnd;
    });

    console.log('📊 Calculating weekly hours:', {
      weekStart: weekStart.toISOString(),
      weekEnd: weekEnd.toISOString(),
      totalEvents: events.length,
      weekEvents: weekEvents.length,
      events: weekEvents.map(e => ({ title: e.title, type: e.type, start: e.start, end: e.end }))
    });

    // Calculate total hours for each type
    const hours = {
      focus: 0,
      tasks: 0,
      target: 0,
      other: 0
    };

    weekEvents.forEach(event => {
      const duration = (event.end.getTime() - event.start.getTime()) / (1000 * 60 * 60); // Convert to hours
      console.log(`Adding ${duration}h for ${event.type}: ${event.title}`);
      hours[event.type] += duration;
    });

    // Calculate total work hours and free time
    const totalWorkHours = hours.focus + hours.tasks + hours.target + hours.other;
    const totalWeekHours = 7 * 24; // 168 hours in a week
    const workingHours = 7 * 17; // Assuming 17 working hours per day (6am-11pm)
    const freeHours = workingHours - totalWorkHours;

    const result = {
      ...hours,
      free: Math.max(0, freeHours)
    };

    console.log('📈 Weekly hours calculated:', result);
    return result;
  }, [currentDate, events]);



  // Generate sample events for the current week
  const getSampleEvents = (weekStartDate: Date): CalendarEvent[] => {
    const weekStart = startOfWeek(weekStartDate);
    const events: CalendarEvent[] = [
      {
        id: 'sample-1',
        title: 'Morning Focus',
        start: new Date(addDays(weekStart, 0).setHours(9, 0, 0, 0)), // Monday 9 AM
        end: new Date(addDays(weekStart, 0).setHours(11, 0, 0, 0)), // Monday 11 AM
        type: 'focus' as const
      },
      {
        id: 'sample-2',
        title: 'Task Review',
        start: new Date(addDays(weekStart, 1).setHours(14, 0, 0, 0)), // Tuesday 2 PM
        end: new Date(addDays(weekStart, 1).setHours(15, 30, 0, 0)), // Tuesday 3:30 PM
        type: 'tasks' as const
      },
      {
        id: 'sample-3',
        title: 'Target Work',
        start: new Date(addDays(weekStart, 2).setHours(10, 0, 0, 0)), // Wednesday 10 AM
        end: new Date(addDays(weekStart, 2).setHours(12, 0, 0, 0)), // Wednesday 12 PM
        type: 'target' as const
      }
    ];
    return events;
  };



  // Load calendar events from Google Calendar
  const loadCalendarEvents = useCallback(async () => {
    const currentSampleEvents = getSampleEvents(currentDate);
    
    if (!gapi || !isSignedIn || !accessToken) {
      // If not connected to Google Calendar, just show sample events
      setEvents(currentSampleEvents.length > 0 ? currentSampleEvents : []);
      return;
    }

    try {
      const weekStart = startOfWeek(currentDate);
      const weekEnd = addDays(weekStart, 6);

      console.log('🔍 Loading Google Calendar events for:', {
        weekStart: weekStart.toISOString(),
        weekEnd: weekEnd.toISOString(),
        isSignedIn,
        hasAccessToken: !!accessToken,
        hasGapi: !!gapi
      });

      const response = await gapi.client.calendar.events.list({
        calendarId: 'primary',
        timeMin: weekStart.toISOString(),
        timeMax: weekEnd.toISOString(),
        showDeleted: false,
        singleEvents: true,
        orderBy: 'startTime'
      });

      console.log('📅 Google Calendar API response:', response.result);
      console.log('📊 Google Calendar events found:', response.result.items?.length || 0);

      const googleEvents: CalendarEvent[] = response.result.items?.map((event: any) => {
        // Parse task type from description
        const description = event.description || '';
        let taskType: 'focus' | 'tasks' | 'target' | 'other' = 'other';
        
        // Look for type in description (e.g., "Type: focus" or "Type:tasks")
        const typeMatch = description.match(/Type:\s*(focus|tasks|target|other)/i);
        if (typeMatch) {
          taskType = typeMatch[1].toLowerCase() as 'focus' | 'tasks' | 'target' | 'other';
        }

        return {
          id: event.id,
          title: event.summary || 'Untitled Event',
          start: new Date(event.start.dateTime || event.start.date),
          end: new Date(event.end.dateTime || event.end.date),
          type: taskType,
          description: event.description
        };
      }) || [];

      console.log('✅ Processed Google events:', googleEvents);
      console.log('🎯 Total events to display:', currentSampleEvents.length + googleEvents.length);

      setEvents([...currentSampleEvents, ...googleEvents]);
    } catch (error) {
      console.error('❌ Error loading calendar events:', error);
      // On error, still show sample events
      setEvents(currentSampleEvents.length > 0 ? currentSampleEvents : []);
    }
  }, [currentDate, gapi, isSignedIn, accessToken]);

  // Initialize Google API and Identity Services
  const initializeGoogleAPIs = useCallback(async () => {
    try {
      if (!GOOGLE_API_KEY || !GOOGLE_CLIENT_ID) {
        console.log('Google Calendar API credentials not configured');
        setConnectionStatus('error');
        return;
      }

      if (!window.gapi || !window.google) {
        console.log('Google APIs not loaded');
        setConnectionStatus('error');
        return;
      }

      setConnectionStatus('connecting');

      // Initialize Google API client
      await new Promise((resolve) => {
        window.gapi.load('client', resolve);
      });

      await window.gapi.client.init({
        apiKey: GOOGLE_API_KEY,
        discoveryDocs: [DISCOVERY_DOC]
      });

             // Initialize Google Identity Services
       window.googleTokenClient = window.google.accounts.oauth2.initTokenClient({
         client_id: GOOGLE_CLIENT_ID,
         scope: SCOPES,
         prompt: 'consent',
         callback: (response: any) => {
           setIsLoading(false);
           if (response.access_token) {
             setAccessToken(response.access_token);
             setIsSignedIn(true);
             setConnectionStatus('connected');
             // Set the access token for API calls
             window.gapi.client.setToken({ access_token: response.access_token });
             loadCalendarEvents();
           } else if (response.error) {
             console.error('OAuth error:', response.error);
             setConnectionStatus('error');
           }
         },
         error_callback: (error: any) => {
           console.error('OAuth initialization error:', error);
           setConnectionStatus('error');
           setIsLoading(false);
         }
       });

      setGapi(window.gapi);
      setIsGoogleApiLoaded(true);
      setConnectionStatus('disconnected');
    } catch (error) {
      console.error('Error initializing Google APIs:', error);
      setConnectionStatus('error');
    }
  }, []);

  // Load Google API script
  useEffect(() => {
    // Load sample events initially for current week
    loadCalendarEvents();

    // Load Google API scripts
    const loadGoogleScripts = async () => {
      // Load Google API script
      if (!window.gapi) {
        await new Promise((resolve, reject) => {
          const script = document.createElement('script');
          script.src = 'https://apis.google.com/js/api.js';
          script.onload = resolve;
          script.onerror = reject;
          document.body.appendChild(script);
        });
      }

      // Load Google Identity Services script
      if (!window.google) {
        await new Promise((resolve, reject) => {
          const script = document.createElement('script');
          script.src = 'https://accounts.google.com/gsi/client';
          script.onload = resolve;
          script.onerror = reject;
          document.body.appendChild(script);
        });
      }

      // Initialize APIs after both scripts are loaded
      await initializeGoogleAPIs();
    };

    loadGoogleScripts().catch((error) => {
      console.error('Failed to load Google scripts:', error);
      setConnectionStatus('error');
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Update events when currentDate changes and user is signedIn
  useEffect(() => {
    loadCalendarEvents();
    // Also update the task form date to match the current viewing week
    updateTaskFormDate();
  }, [currentDate, loadCalendarEvents]);

  // Update weekly hours when events or currentDate changes
  useEffect(() => {
    const updatedHours = calculateWeeklyHours();
    setWeeklyHours(updatedHours);
  }, [calculateWeeklyHours]);

  // Sign in to Google using new Identity Services
  const handleSignIn = async () => {
    if (!window.googleTokenClient) {
      console.error('Google token client not initialized');
      return;
    }
    
    try {
      setIsLoading(true);
      setConnectionStatus('connecting');
      
      // Check if user has existing valid token
      if (accessToken) {
        // Test if current token is still valid
        try {
          await window.gapi.client.calendar.calendarList.list();
          setConnectionStatus('connected');
          setIsLoading(false);
          return;
        } catch (e) {
          // Token expired, continue with new auth
          setAccessToken(null);
          window.gapi.client.setToken(null);
        }
      }
      
      // Request new access token
      window.googleTokenClient.requestAccessToken({
        prompt: 'consent'
      });
    } catch (error) {
      console.error('Error signing in:', error);
      setConnectionStatus('error');
      setIsLoading(false);
    }
  };

  // Sign out from Google
  const handleSignOut = async () => {
    try {
      if (accessToken) {
        // Revoke the token
        window.google.accounts.oauth2.revoke(accessToken);
      }
      
      // Clear local state
      setAccessToken(null);
      setIsSignedIn(false);
      setConnectionStatus('disconnected');
      
      // Clear gapi token
      if (window.gapi && window.gapi.client) {
        window.gapi.client.setToken(null);
      }

      // Reload events (will show only sample events now)
      await loadCalendarEvents();
    } catch (error) {
      console.error('Error signing out:', error);
    }
  };

  // Create new task (local or Google Calendar)
  const createTask = async () => {
    if (!taskForm.title.trim()) {
      alert('Please enter a task title');
      return;
    }

    try {
      setIsLoading(true);

      // Parse due date and time
      const [hours, minutes] = taskForm.dueTime.split(':');
      const dueDateTime = new Date(taskForm.dueDate);
      dueDateTime.setHours(parseInt(hours), parseInt(minutes), 0, 0);
      const endDateTime = new Date(dueDateTime.getTime() + (taskForm.duration * 60 * 60 * 1000));

      // Create local event first
      const systemDescription = `Duration: ${taskForm.duration}h\nType: ${taskForm.type}`;
      const fullDescription = taskForm.description.trim() 
        ? `${taskForm.description}\n\n${systemDescription}`
        : systemDescription;

      const newEvent: CalendarEvent = {
        id: `local-${Date.now()}`,
        title: taskForm.title,
        start: dueDateTime,
        end: endDateTime,
        type: taskForm.type,
        description: fullDescription
      };

      // Add to local events
      setEvents(prevEvents => [...prevEvents, newEvent]);

      // If Google Calendar is connected, also create there
      if (gapi && isSignedIn && accessToken) {
        try {
          const event = {
            summary: taskForm.title,
            start: {
              dateTime: dueDateTime.toISOString(),
              timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone
            },
            end: {
              dateTime: endDateTime.toISOString(),
              timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone
            },
            description: newEvent.description
          };

          await gapi.client.calendar.events.insert({
            calendarId: 'primary',
            resource: event
          });

          // Reload events to get the Google Calendar event ID
          await loadCalendarEvents();
        } catch (googleError) {
          console.error('Error creating Google Calendar event:', googleError);
          alert('Task created locally, but failed to sync with Google Calendar');
        }
      }

      // Reset form
      setTaskForm({
        ...taskForm,
        title: '',
        description: ''
      });

      alert('Task created successfully!');
    } catch (error) {
      console.error('Error creating task:', error);
      alert('Error creating task. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Navigation functions
  const goToPreviousWeek = () => setCurrentDate(subWeeks(currentDate, 1));
  const goToNextWeek = () => setCurrentDate(addWeeks(currentDate, 1));

  // Get week days
  const getWeekDays = () => {
    const start = startOfWeek(currentDate);
    return Array.from({ length: 7 }, (_, i) => addDays(start, i));
  };

  // Time slots (6am to 11pm)
  const timeSlots = Array.from({ length: 18 }, (_, i) => i + 6);

  // Get events that START in this specific hour slot (to avoid duplicates)
  const getEventsForSlot = (day: Date, hour: number) => {
    const filteredEvents = events.filter(event => {
      const eventStart = new Date(event.start);
      const eventDate = format(eventStart, 'yyyy-MM-dd');
      const dayDate = format(day, 'yyyy-MM-dd');
      
      // Only show events that start in this specific hour and are on this specific day
      return eventDate === dayDate && eventStart.getHours() === hour;
    });

    return filteredEvents;
  };

  // Calculate task block position and height spanning multiple hours if needed
  const getTaskBlockStyle = (event: CalendarEvent, hour: number) => {
    const eventStart = new Date(event.start);
    const eventEnd = new Date(event.end);
    
    // Calculate position within the starting hour
    const startMinutes = eventStart.getMinutes();
    const topPosition = (startMinutes / 60) * 100;
    
    // Calculate total duration in minutes
    const durationMinutes = (eventEnd.getTime() - eventStart.getTime()) / (1000 * 60);
    
    // Calculate height in terms of calendar grid units (each hour = 100% of a cell)
    const heightPercentage = (durationMinutes / 60) * 100;
    
    return {
      top: `${topPosition}%`,
      height: `${heightPercentage}%`,
      position: 'absolute' as const,
      width: '90%', // Leave some margin for readability
      left: '5%',
      zIndex: 10
    };
  };

  // Get connection status message
  const getConnectionStatusMessage = () => {
    switch (connectionStatus) {
      case 'connected':
        return '✓ Connected to Google Calendar';
      case 'connecting':
        return '⏳ Connecting to Google Calendar...';
      case 'error':
        return '❌ Google Calendar API not configured';
      default:
        return '⚠ Not connected to Google Calendar';
    }
  };

  return (
    <div className="calendar-planner">
      {/* Main Calendar Container */}
      <div className="calendar-container">
        {/* Header */}
        <div className="calendar-header">
          <h1 className="planner-title">Calendar Planner</h1>
          <div className="calendar-nav">
            <button className="nav-btn" onClick={goToPreviousWeek}>←</button>
            <button className="nav-btn" onClick={goToNextWeek}>→</button>
            <span className="month-year">{format(currentDate, 'MMMM yyyy')}</span>
          </div>
        </div>

        {/* Calendar Content */}
        <div className="calendar-content">
          {/* Legend */}
          <div className="calendar-legend">
            {(() => {
              if (Object.values(weeklyHours).every(value => value === 0)) {
                return <span>No events found for this week.</span>;
              }
              return (
                <>
                  <div className="legend-item">
                    <div className="legend-color focus"></div>
                    <span>Focus {weeklyHours.focus.toFixed(1)}h</span>
                  </div>
                  <div className="legend-item">
                    <div className="legend-color tasks"></div>
                    <span>Tasks {weeklyHours.tasks.toFixed(1)}h</span>
                  </div>
                  <div className="legend-item">
                    <div className="legend-color target"></div>
                    <span>Focus target {weeklyHours.target.toFixed(1)}h</span>
                  </div>
                  <div className="legend-item">
                    <div className="legend-color other"></div>
                    <span>Other work {weeklyHours.other.toFixed(1)}h</span>
                  </div>
                  <div className="legend-item">
                    <div className="legend-color free"></div>
                    <span>Free {weeklyHours.free.toFixed(1)}h</span>
                  </div>
                </>
              );
            })()}
          </div>

          {/* Calendar Grid */}
          <div className="calendar-grid">
            {/* Time header */}
            <div className="time-header">GMT+3</div>
            
            {/* Day headers */}
            {getWeekDays().map((day, index) => (
              <div 
                key={index} 
                className={`day-header ${isToday(day) ? 'today' : ''}`}
              >
                <div>{format(day, 'EEE d')}</div>
              </div>
            ))}

            {/* Time slots and calendar cells */}
            {timeSlots.map(hour => (
              <React.Fragment key={hour}>
                {/* Time slot label */}
                <div className="time-slot">
                  {hour === 6 ? '6am' : hour === 12 ? '12pm' : hour === 23 ? '11pm' : hour > 12 ? `${hour-12}pm` : `${hour}am`}
                </div>
                
                {/* Calendar cells for each day */}
                {getWeekDays().map((day, dayIndex) => {
                  const eventsInSlot = getEventsForSlot(day, hour);
                  
                  return (
                    <div key={`${hour}-${dayIndex}`} className="calendar-cell">
                      {eventsInSlot.map(event => (
                        <div
                          key={event.id}
                          className={`task-block ${event.type}`}
                          style={getTaskBlockStyle(event, hour)}
                          title={event.title}
                        >
                          {event.title}
                        </div>
                      ))}
                    </div>
                  );
                })}
              </React.Fragment>
            ))}
          </div>
        </div>
      </div>

      {/* Task Creation Sidebar */}
      <div className="task-sidebar">
        <div className="sidebar-header">
          <h2 className="sidebar-title">Create New Task</h2>
        </div>

        {/* Google Calendar API Status */}
        <div className={`api-status ${connectionStatus}`}>
          {getConnectionStatusMessage()}
        </div>



        {connectionStatus === 'disconnected' && isGoogleApiLoaded && (
          <button className="connect-btn" onClick={handleSignIn} disabled={isLoading}>
            {isLoading ? 'Connecting...' : 'Connect Google Calendar'}
          </button>
        )}

        {connectionStatus === 'error' && (
          <button 
            className="connect-btn" 
            onClick={() => {
              setConnectionStatus('disconnected');
              window.location.reload();
            }}
            style={{background: '#ffc107', color: '#000'}}
          >
            Reload & Retry
          </button>
        )}

        {connectionStatus === 'connected' && (
          <button className="connect-btn disconnect-btn" onClick={handleSignOut}>
            Disconnect Google Calendar
          </button>
        )}

        {connectionStatus === 'error' && (
          <div className="error-message">
            <strong>Google Calendar Connection Issue</strong>
            <br />
            <br />If you see popup blocked or CORS errors:
            <br />1. Allow popups for this site in your browser
            <br />2. Make sure your OAuth client is configured for http://localhost:3000
            <br />3. Try refreshing the page and connecting again
            <br />
            <br />For API setup:
            <br />1. Get credentials from: <a href="https://console.cloud.google.com/" target="_blank" rel="noopener noreferrer">Google Cloud Console</a>
            <br />2. Add to .env file: REACT_APP_GOOGLE_API_KEY and REACT_APP_GOOGLE_CLIENT_ID
            <br />3. Add http://localhost:3000 to authorized origins
            <br />4. Restart the development server
          </div>
        )}

        {/* Task Form */}
        <div className="form-group">
          <input
            type="text"
            className="form-input"
            placeholder="Task name..."
            value={taskForm.title}
            onChange={(e) => setTaskForm({...taskForm, title: e.target.value})}
          />
        </div>

        <div className="form-group">
          <label className="form-label">Duration</label>
          <div className="duration-controls">
            <button 
              className="duration-btn"
              onClick={() => setTaskForm({...taskForm, duration: Math.max(0.5, taskForm.duration - 0.5)})}
            >
              -
            </button>
            <input
              type="text"
              className="duration-input"
              value={`${taskForm.duration} hr`}
              readOnly
            />
            <button 
              className="duration-btn"
              onClick={() => setTaskForm({...taskForm, duration: taskForm.duration + 0.5})}
            >
              +
            </button>
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Task Type</label>
          <select 
            className="form-input"
            value={taskForm.type}
            onChange={(e) => setTaskForm({...taskForm, type: e.target.value as 'focus' | 'tasks' | 'target' | 'other'})}
          >
            <option value="focus">Focus</option>
            <option value="tasks">Tasks</option>
            <option value="target">Focus target</option>
            <option value="other">Other work</option>
          </select>
        </div>

        <div className="form-group">
          <label className="form-label">Description (for Google Calendar)</label>
          <textarea
            className="form-input"
            placeholder="Optional description for Google Calendar..."
            value={taskForm.description}
            onChange={(e) => setTaskForm({...taskForm, description: e.target.value})}
            rows={3}
            style={{resize: 'vertical', minHeight: '60px'}}
          />
        </div>

        <div className="form-group">
          <label className="form-label">Due date & time</label>
          <div className="datetime-inputs">
            <input
              type="date"
              className="schedule-input"
              value={taskForm.dueDate}
              onChange={(e) => setTaskForm({...taskForm, dueDate: e.target.value})}
            />
            <input
              type="time"
              className="schedule-input"
              value={taskForm.dueTime}
              onChange={(e) => setTaskForm({...taskForm, dueTime: e.target.value})}
            />
          </div>
          <div style={{fontSize: '12px', color: '#666', marginTop: '5px', display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
            <span>📅 {format(new Date(taskForm.dueDate), 'EEEE, MMMM d, yyyy')} at {taskForm.dueTime}</span>
            <button 
              type="button"
              style={{fontSize: '10px', padding: '2px 6px', background: '#007bff', color: 'white', border: 'none', borderRadius: '3px', cursor: 'pointer'}}
              onClick={() => setTaskForm({...taskForm, dueDate: format(new Date(), 'yyyy-MM-dd')})}
            >
              Today
            </button>
          </div>
        </div>

        <button 
          className="create-btn" 
          onClick={createTask}
          disabled={!taskForm.title.trim() || isLoading}
        >
          {isLoading ? 'Creating...' : 'Create Task'}
        </button>
      </div>
    </div>
  );
};

export default Calendar;