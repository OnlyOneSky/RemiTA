import React, { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
} from 'react-native';

export default function HomeScreen({ route, navigation }) {
  const { displayName = 'User' } = route.params || {};
  const [menuVisible, setMenuVisible] = useState(false);

  const handleLogout = () => {
    navigation.replace('Login');
  };

  return (
    <View style={styles.container}>
      {/* Welcome message */}
      <Text
        accessibilityLabel="welcome_message"
        testID="welcome_message"
        style={styles.welcome}
      >
        Welcome, {displayName}!
      </Text>

      <Text style={styles.body}>
        You are now logged in to the RemiTA sample app.
      </Text>

      {/* Menu button */}
      <TouchableOpacity
        accessibilityLabel="menu_button"
        testID="menu_button"
        style={styles.menuButton}
        onPress={() => setMenuVisible(!menuVisible)}
      >
        <Text style={styles.menuButtonText}>☰ Menu</Text>
      </TouchableOpacity>

      {/* Dropdown menu */}
      {menuVisible && (
        <View style={styles.menu}>
          <TouchableOpacity
            accessibilityLabel="logout_button"
            testID="logout_button"
            style={styles.menuItem}
            onPress={handleLogout}
          >
            <Text style={styles.menuItemText}>Logout</Text>
          </TouchableOpacity>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
    backgroundColor: '#f5f5f5',
  },
  welcome: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 12,
    textAlign: 'center',
  },
  body: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginBottom: 40,
  },
  menuButton: {
    backgroundColor: '#4a90d9',
    borderRadius: 8,
    paddingVertical: 14,
    paddingHorizontal: 32,
  },
  menuButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '600',
  },
  menu: {
    marginTop: 16,
    backgroundColor: '#fff',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#ddd',
    width: 200,
  },
  menuItem: {
    padding: 16,
    alignItems: 'center',
  },
  menuItemText: {
    fontSize: 16,
    color: '#e74c3c',
    fontWeight: '500',
  },
});
