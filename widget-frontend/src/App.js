// src/App.js
import { useState, useEffect, useRef } from 'react';
import { MantineProvider, Card, Text, Button, TextInput, Paper, ActionIcon, Group, ScrollArea } from '@mantine/core';
import { IconX, IconMessageCircle, IconSend } from '@tabler/icons-react';

const WS_URL = 'ws://localhost:8000/ws';

// === Компонент одного сообщения в чате ===
function Message({ message }) {
  const isUser = message.sender === 'user';
  return (
    <Paper
      withBorder
      p="xs"
      radius="md"
      style={{
        backgroundColor: isUser ? '#228be6' : '#e9ecef', // синий для юзера, серый для бота
        color: isUser ? 'white' : 'black',
        alignSelf: isUser ? 'flex-end' : 'flex-start', // справа для юзера, слева для бота
        maxWidth: '80%',
      }}
    >
      <Text size="sm">{message.text}</Text>
    </Paper>
  );
}


// === Основной компонент виджета (сам чат) ===
function ChatWidget({ onClose }) {
  // Состояние для сообщений и статуса диалога
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isFinished, setIsFinished] = useState(false);
  const [vacancyId, setVacancyId] = useState(null); // <-- 1. Добавляем состояние для ID вакансии
  const [resumeId, setResumeId] = useState(null); // <-- Новое состояние для ID резюме
  const socket = useRef(null);
  const viewport = useRef(null); // Для авто-прокрутки

  // Функция для автоматической прокрутки вниз
  const scrollToBottom = () => {
    viewport.current.scrollTo({ top: viewport.current.scrollHeight, behavior: 'smooth' });
  };

  // --- ЛОГИКА РАБОТЫ С LOCALSTORAGE ---

  // <-- 2. Добавляем useEffect для чтения ID вакансии из HTML
  useEffect(() => {
    const vacancyElement = document.getElementById('vacancy-id');
    if (vacancyElement) {
      setVacancyId(vacancyElement.value);
      console.log("Найден ID вакансии:", vacancyElement.value);
    } else {
      console.warn("Элемент с id 'vacancy-id' не найден на странице.");
    }

    const resumeElement = document.getElementById('resume-id');
    if (resumeElement) {
      setResumeId(resumeElement.value);
      console.log("Найден ID резюме:", resumeElement.value);
    } else {
      console.warn("Элемент с id 'resume-id' не найден на странице.");
    }
  }, []); // Пустой массив зависимостей, чтобы выполнилось один раз при монтировании

  // 1. ЗАГРУЗКА истории из localStorage при открытии виджета
  useEffect(() => {
    const savedMessages = localStorage.getItem('chat_messages');
    if (savedMessages) {
      setMessages(JSON.parse(savedMessages));
    }
    const savedIsFinished = localStorage.getItem('chat_finished');
    if (savedIsFinished === 'true') {
      setIsFinished(true);
    }
  }, []);

  // 2. СОХРАНЕНИЕ истории в localStorage при любом изменении
  useEffect(() => {
    localStorage.setItem('chat_messages', JSON.stringify(messages));
    localStorage.setItem('chat_finished', isFinished);
    if (messages.length > 0) {
      scrollToBottom();
    }
  }, [messages, isFinished]);


  // --- ЛОГИКА РАБОТЫ С WEBSOCKET ---
  useEffect(() => {
    socket.current = new WebSocket(WS_URL);
    socket.current.onopen = () => {
      console.log('WS соединение установлено');
      // --- NEW: Send initial message to trigger AI ---
      // We use a timeout to ensure vacancyId/resumeId have been set from the other useEffect
      setTimeout(() => {
        setMessages(prev => {
          // Only send the initial message if the chat is empty
          if (prev.length === 0 && vacancyId && resumeId) {
            console.log("Отправка стартового сообщения для начала диалога с AI");
            socket.current.send(JSON.stringify({ text: 'start', vacancy_id: vacancyId, resume_id: resumeId }));
          }
          return prev;
        });
      }, 100); // A small delay is usually sufficient
    };

    socket.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      const botMessage = { text: data.message, sender: 'bot' };
      setMessages(prev => [...prev, botMessage]);

      // Если бэкенд сказал завершить диалог
      if (data.finish_conversation === true) {
        setIsFinished(true);
        socket.current.close();
      }
    };

    socket.current.onclose = () => console.log('WS соединение закрыто');
    return () => socket.current.close();
  }, [vacancyId, resumeId]); // Rerun if IDs change (though they shouldn't in this setup)

  const sendMessage = () => {
    if (!inputValue.trim() || isFinished) return;

    const userMessage = { text: inputValue, sender: 'user' };
    setMessages(prev => [...prev, userMessage]);
    
    // <-- 3. Формируем и отправляем JSON вместо простого текста
    if (socket.current.readyState === WebSocket.OPEN) {
      const messagePayload = {
        text: inputValue,
        vacancy_id: vacancyId, // Добавляем ID вакансии в отправляемые данные
        resume_id: resumeId // Добавляем ID резюме
      };
      socket.current.send(JSON.stringify(messagePayload));
    }
    setInputValue('');
  };

  return (
    <Card
      shadow="xl"
      p="lg"
      radius="md"
      withBorder
      style={{ width: 350, height: 500, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}
    >
      <Group position="apart" mb="md">
        <Text weight={500}>Чат-поддержка</Text>
        <ActionIcon onClick={onClose}><IconX size={16} /></ActionIcon>
      </Group>

      {/* Message Area: The key is to make this a flex item that can shrink and has its own overflow handling. */}
      <ScrollArea style={{ flex: '1 1 0', minHeight: 0, marginBottom: '10px' }} viewportRef={viewport}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {messages.map((msg, index) => <Message key={index} message={msg} />)}
        </div>
      </ScrollArea>

      {/* Область ввода */}
      {isFinished ? (
        <Text color="dimmed" align="center" size="sm">Диалог завершен.</Text>
      ) : (
        <Group noWrap>
          <TextInput
            placeholder="Введите 'bye' для завершения"
            value={inputValue}
            onChange={(event) => setInputValue(event.currentTarget.value)}
            onKeyDown={(event) => event.key === 'Enter' && sendMessage()}
            style={{ flex: 1 }}
            disabled={isFinished}
          />
          <Button onClick={sendMessage} disabled={isFinished}><IconSend size={16}/></Button>
        </Group>
      )}
    </Card>
  );
}


// === Компонент-обертка, который управляет состоянием ===
function App() {
  const [isOpen, setIsOpen] = useState(false);

  const handleClose = () => {
    // ОЧИЩАЕМ ВСЕ ДАННЫЕ ПРИ ЗАКРЫТИИ
    localStorage.removeItem('chat_messages');
    localStorage.removeItem('chat_finished');
    setIsOpen(false);
  };

  const widgetContainerStyle = {
    position: 'fixed',
    bottom: '20px',
    right: '20px',
    zIndex: 1000,
  };

  return (
    <div style={widgetContainerStyle}>
      {isOpen ? (
        <ChatWidget onClose={handleClose} />
      ) : (
        <Button onClick={() => setIsOpen(true)} radius="xl" size="lg" shadow="xl">
          <IconMessageCircle size={24} />
        </Button>
      )}
    </div>
  );
}

// Рендерим все с провайдером Mantine
export default function MantineApp() {
  return (
    <MantineProvider withGlobalStyles withNormalizeCSS>
      <App />
    </MantineProvider>
  );
}