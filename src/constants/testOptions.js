// Test options configuration - pure data without JSX
export const TEST_OPTIONS = [
  { 
    id: 1,
    label: 'Session Reminder', 
    test_types: [
      "Ensure that session reminders pop up in game",
      "Ensure that the continue button takes you back to the game",
      "Ensure that the Exit Game button takes you to the lobby",
      "Ensure that when the session reminder pops up, the game does not continue in the background",
      "Ensure that when the session reminder pops up, the free spins game does not malfunction",
      "Ensure that when the session reminder pops up, the Bonus game does not malfunction"
    ],
    iconName: 'ShieldCheck',
    iconColor: 'text-green-400',
    description: 'Test session reminder functionality'
  },
  { 
    id: 2,
    label: 'Playcheck Regulation – limited to the base game', 
    test_types: ["Playcheck Regulation – limited to the base game"], 
    iconName: 'RotateCcw',
    iconColor: 'text-blue-400',
    description: 'Verify playcheck regulation compliance for base game'
  },
  { 
    id: 3,
    label: 'Multiple Spin Test – limited to the base game', 
    test_types: ["Multiple Spin Test – limited to the base game"], // No exact match in Section column
    iconName: 'Repeat',
    iconColor: 'text-blue-400',
    description: 'Test multiple spin functionality in base game'
  },
  {
    id: 4, 
    label: 'Banking', 
    test_types: [
      "Menu - Banking Option Works",
      "Player can successfully Deposit and Credit Balance updates correctly"
    ],
    iconName: 'Banknote',
    iconColor: 'text-green-400',
    description: 'Verify banking and payment compliance'
  },
  { 
    id: 5,
    label: 'Practice Play', 
    test_types: [
      "Play for Real Banner Displays and Fades Out"
    ],
    iconName: 'PlayCircle',
    iconColor: 'text-blue-400',
    description: 'Test practice play mode functionality'
  },
  { 
    id: 6,
    label: 'Max Bet Limit Testing', 
    test_types: [
      "Max Bet of £6.35",
      "Max Bet of £5.00",
      "Max Bet of £3.00",
      "Max Bet of £2.00",
      "Max Bet of £1.75"
    ],
    iconName: 'Maximize2',
    iconColor: 'text-green-400',
    description: 'Verify maximum bet limit restrictions'
  },
  { 
    id: 7,
    label: 'Regression Testing', 
    test_types: ["Regression Testing"], 
    iconName: 'Maximize2',
    iconColor: 'text-green-400',
    description: 'Run regression tests to ensure compliance with previous standards'
  }
];
