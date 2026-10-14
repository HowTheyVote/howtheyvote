import tutorials from "../data/tutorials.json";
import Card from "./Card";
import Stack from "./Stack";

function Tutorials() {
  return (
    <Stack space="sm">
      {tutorials.map(({ url, title, description }) => (
        <Card
          title={title}
          link={url}
          description={description}
          clickable={false}
          external={true}
        />
      ))}
    </Stack>
  );
}

export default Tutorials;
