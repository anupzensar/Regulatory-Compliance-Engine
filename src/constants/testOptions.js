// Government policies configuration
export const GOVERNMENT_POLICIES = [
  { value: 'uk', label: 'United Kingdom' },
  { value: 'alderney', label: 'Alderney' },
  { value: 'usa', label: 'United States' },
  { value: 'brazil', label: 'Brazil' },
  { value: 'malta', label: 'Malta' },
  { value: 'gibraltar', label: 'Gibraltar' },
  { value: 'curacao', label: 'Curacao' }
];

// Test suites configuration
export const TEST_SUITES = [
  {
    label: 'Session Reminder',
    value: 'session_reminder',
    description: 'Test session reminder functionality',
    test_cases: [
      {
        id: 'sr_001',
        name: 'Session Reminder Pop-up Test',
        description: 'Ensure that session reminders pop up in game'
      },
      {
        id: 'sr_002',
        name: 'Continue Button Test',
        description: 'Ensure that the continue button takes you back to the game'
      },
      {
        id: 'sr_003',
        name: 'Exit Game Button Test',
        description: 'Ensure that the Exit Game button takes you to the lobby'
      },
      {
        id: 'sr_004',
        name: 'Background Game Pause Test',
        description: 'Ensure that when the session reminder pops up, the game does not continue in the background'
      }
    ]
  },
  {
    label: 'Playcheck Regulation – limited to the base game',
    value: 'playcheck_regulation',
    description: 'Verify playcheck regulation compliance for base game',
    test_cases: [
      {
        id: 'pr_001',
        name: 'Base Game Playcheck Test',
        description: 'Comprehensive testing of playcheck regulation in base game only'
      },
      {
        id: 'pr_002',
        name: 'Bonus Feature Restriction Test',
        description: 'Ensure bonus features are properly restricted during playcheck'
      }
    ]
  },
  {
    label: 'Multiple Spin Test – limited to the base game',
    value: 'multiple_spin',
    description: 'Test multiple spin functionality in base game',
    test_cases: [
      {
        id: 'ms_001',
        name: 'Multiple Spin Execution Test',
        description: 'Test multiple consecutive spins in base game'
      },
      {
        id: 'ms_002',
        name: 'RTP Verification Test',
        description: 'Verify return to player percentage across multiple spins'
      }
    ]
  },
  {
    label: 'Banking',
    value: 'banking',
    description: 'Verify banking and payment compliance',
    test_cases: [
      {
        id: 'b_001',
        name: 'Banking Menu Test',
        description: 'Menu - Banking Option Works'
      },
      {
        id: 'b_002',
        name: 'Deposit Functionality Test',
        description: 'Player can successfully Deposit and Credit Balance updates correctly'
      }
    ]
  },
  {
    label: 'Practice Play',
    value: 'practice_play',
    description: 'Test practice play mode functionality',
    test_cases: [
      {
        id: 'pp_001',
        name: 'Play for Real Banner Test',
        description: 'Play for Real Banner Displays and Fades Out'
      },
      {
        id: 'pp_002',
        name: 'Demo Mode Verification Test',
        description: 'Verify demo mode functionality and restrictions'
      }
    ]
  },
  {
    label: 'Max Bet Limit Testing',
    value: 'max_bet_limit',
    description: 'Verify maximum bet limit restrictions',
    test_cases: [
      {
        id: 'mbl_001',
        name: 'Max Bet £6.35 Test',
        description: 'Max Bet of £6.35'
      },
      {
        id: 'mbl_002',
        name: 'Max Bet £5.00 Test',
        description: 'Max Bet of £5.00'
      },
      {
        id: 'mbl_003',
        name: 'Max Bet £3.00 Test',
        description: 'Max Bet of £3.00'
      }
    ]
  },
  {
    label: 'Regression',
    value: 'regression',
    description: 'Run regression tests to ensure compliance with previous standards',
    test_cases: [
      {
        id: 'r_001',
        name: 'UI Elements Regression Test',
        description: 'Verify all UI elements are working as expected'
      }
    ]
  }
];