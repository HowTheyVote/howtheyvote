import showcase from "../data/showcase.json";
import Card from "./Card";
import Stack from "./Stack";

function Showcase() {
  return (
    <Stack space="sm">
      {showcase.map(({ url, title, author, description }) => (
        <Card
          title={title}
          subtitle={author}
          description={description}
          link={url}
          clickable={false}
        />
      ))}
    </Stack>
  );
}

export default Showcase;
