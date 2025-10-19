import { useState, useEffect } from 'react';
import { 
  Container, 
  Grid, 
  Card, 
  Text, 
  Group, 
  Badge, 
  Progress, 
  Table,
  TextInput,
  Select,
  Stack,
  Avatar
} from '@mantine/core';
import { IconSearch, IconStar, IconMessage } from '@tabler/icons-react';

function EmployerDashboard() {
  const [analyses, setAnalyses] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterScore, setFilterScore] = useState('all');

  useEffect(() => {
    // Загрузка анализов с бэкенда
    fetch('/api/analyses')
      .then(res => res.json())
      .then(setAnalyses);
  }, []);

  const filteredAnalyses = analyses.filter(analysis => {
    const matchesSearch = analysis.summary.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesScore = filterScore === 'all' || 
      (filterScore === 'high' && analysis.final_score >= 80) ||
      (filterScore === 'medium' && analysis.final_score >= 50 && analysis.final_score < 80) ||
      (filterScore === 'low' && analysis.final_score < 50);
    
    return matchesSearch && matchesScore;
  });

  const getScoreColor = (score) => {
    if (score >= 80) return 'green';
    if (score >= 60) return 'yellow';
    return 'red';
  };

  return (
    <Container size="xl" py="xl">
      <Stack spacing="xl">
        <Group position="apart">
          <div>
            <Text size="xl" weight={700}>Кандидаты</Text>
            <Text color="dimmed">Анализ соответствия вакансиям</Text>
          </div>
          <Group>
            <TextInput
              placeholder="Поиск по кандидатам..."
              icon={<IconSearch size={16} />}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <Select
              placeholder="Фильтр по релевантности"
              value={filterScore}
              onChange={setFilterScore}
              data={[
                { value: 'all', label: 'Все кандидаты' },
                { value: 'high', label: 'Высокая (80%+)' },
                { value: 'medium', label: 'Средняя (50-79%)' },
                { value: 'low', label: 'Низкая (<50%)' },
              ]}
            />
          </Group>
        </Group>

        <Grid>
          {filteredAnalyses.map((analysis) => (
            <Grid.Col key={analysis.analysis_id} span={4}>
              <Card shadow="sm" p="lg" radius="md" withBorder>
                <Group position="apart" mb="xs">
                  <Avatar color="blue" radius="xl">
                    {analysis.candidate_id.slice(-2)}
                  </Avatar>
                  <Badge 
                    color={getScoreColor(analysis.final_score)} 
                    variant="filled"
                  >
                    {analysis.final_score}%
                  </Badge>
                </Group>

                <Progress
                  value={analysis.final_score}
                  color={getScoreColor(analysis.final_score)}
                  size="lg"
                  radius="xl"
                  mb="md"
                />

                <Text size="sm" color="dimmed" lineClamp={3}>
                  {analysis.summary}
                </Text>

                <Group position="apart" mt="md">
                  <Badge variant="outline" size="sm">
                    <IconMessage size={12} style={{ marginRight: 4 }} />
                    {analysis.conversation.length} сообщ.
                  </Badge>
                  <Text size="xs" color="dimmed">
                    {new Date(analysis.created_at).toLocaleDateString()}
                  </Text>
                </Group>
              </Card>
            </Grid.Col>
          ))}
        </Grid>
      </Stack>
    </Container>
  );
}

export default EmployerDashboard;