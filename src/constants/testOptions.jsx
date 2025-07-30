// Test options configuration - pure data without JSX
export const TEST_OPTIONS = [
  { 
    label: 'Session Reminder', 
    iconName: 'ShieldCheck',
    iconColor: 'text-green-400',
    description: 'Test session reminder functionality'
  },
  { 
    label: 'Playcheck Regulation – limited to the base game', 
    iconName: 'RotateCcw',
    iconColor: 'text-blue-400',
    description: 'Verify playcheck regulation compliance for base game'
  },
  { 
    label: 'Multiple Spin Test – limited to the base game', 
    iconName: 'Repeat',
    iconColor: 'text-blue-400',
    description: 'Test multiple spin functionality in base game'
  },
  { 
    label: 'Banking', 
    iconName: 'Banknote',
    iconColor: 'text-green-400',
    description: 'Verify banking and payment compliance'
  },
  { 
    label: 'Practice Play', 
    iconName: 'PlayCircle',
    iconColor: 'text-blue-400',
    description: 'Test practice play mode functionality'
  },
  { 
    label: 'Max Bet Limit Testing', 
    iconName: 'Maximize2',
    iconColor: 'text-green-400',
    description: 'Verify maximum bet limit restrictions'
  },
  { 
    label: 'Regression Testing', 
    iconName: 'Maximize2',
    iconColor: 'text-green-400',
    description: 'Run regression tests to ensure compliance with previous standards'
  },
];

// URL validation regex
export const URL_REGEX = /^https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&=]*)$/;
