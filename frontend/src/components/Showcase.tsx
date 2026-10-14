import showcase from "../data/showcase.json";
import Card from "./Card";
import Stack from "./Stack";

type ShowcaseProps = {
  category: "research" | "journalism" | "nonprofit";
};

function Showcase({ category }: ShowcaseProps) {
  return (
    <Stack space="sm">
      {showcase[category].map(({ url, title, author, description }) => (
        <Card
          title={title}
          subtitle={author}
          description={description}
          link={url}
          clickable={false}
          external={true}
        />
      ))}
    </Stack>
  );
}

export default Showcase;
